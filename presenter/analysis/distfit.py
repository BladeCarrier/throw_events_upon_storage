"""
**hep_ml.distfit** is minimalistic and very flexible distribution fitter.
It is based on writing pdf expression using formulaes not objects.

Technical base: `theano` for writing pdf expression and `scipy.optimize`
to solve maximization problem.

Apart from this, sPlot implementation is present here.

"""


from __future__ import division, absolute_import
from collections import OrderedDict
import inspect

import numpy
np = numpy
import pandas
import theano
import theano.tensor as T

from hep_ml.commonutils import check_sample_weight
from scipy.optimize import minimize


floatX = theano.config.floatX

__author__ = 'Alex Rogozhnikov'


def gauss(x, mean, sigma):
    """gauss distribution"""
    t = (x - mean) / sigma
    return T.exp(- t ** 2 / 2.) / (numpy.sqrt(2 * numpy.pi) * sigma)


def exponential(x, slope):
    """exponential distribution"""
    return T.exp(- slope * x) * slope * (x > 0)


def uniform(x, left, right):
    """uniform distribution"""
    return (x > left) * (x < right) / (right - left)


def gap(x, left, right):
    """Needed for fitting with blind region """
    return (x < left) + (x > right)


def crystal_ball(x, mean, sigma, alpha, power):
    """Not computing normalization here"""
    u = (x - mean) / sigma
    p, a = power, alpha
    A = ((p / abs(a)) ** p) * T.exp(-a * a / 2.)
    B = p / abs(a) - abs(a)

    result_right = A * (B + u) ** (-p)
    result_center = T.exp(-u ** 2 / 2.)

    result = T.switch(u < alpha, result_center, result_right)
    return result


def crystal_ball_2sided(x, mean, sigma, alpha_left, power_left, alpha_right, power_right):
    """Not computing normalization here, adopted from
    https://github.com/cms-analysis/JetMETAnalysis-JetAnalyzers/blob/master/bin/jet_response_fitter_x.cc"""
    u = (x - mean) / sigma
    p1, p2 = power_left, power_right
    a1, a2 = alpha_left, alpha_right
    A1 = ((p1 / abs(a1)) ** p1) * T.exp(-a1 * a1 / 2.)
    A2 = ((p2 / abs(a2)) ** p2) * T.exp(-a2 * a2 / 2.)
    B1 = p1 / abs(a1) - abs(a1)
    B2 = p2 / abs(a2) - abs(a2)

    result_left = A1 * (B1 - u) ** (-p1)
    result_right = A2 * (B2 + u) ** (-p2)
    result_center = T.exp(-u ** 2 / 2.)

    result = T.switch(u < - alpha_right, result_left,
                      T.switch(u < alpha_right, result_center, result_right))
    return result


class DistributionsMixture(object):
    def __init__(self, distributions, parameter_ranges, column_ranges, weights_ranges, sampling_strategy='grid'):
        """
        Mixture fitter fits linear combination of several distributions (say, a * gauss + b * exponent)

        :param distributions: fitted distributions,
        :param parameter_ranges: in which range each parameter is charged
        :param column_ranges: in which range each of variables participated in fitting should be
            (it's the integration volume)
        :param weights_ranges: ranges for all distributions (floats from 0 to 1).
        """
        self.distributions = OrderedDict(distributions)
        self.column_ranges = OrderedDict(column_ranges)
        self._initial_parameter_ranges = OrderedDict(parameter_ranges)
        self.weight_ranges = weights_ranges
        self.random_state = numpy.random.RandomState(42)
        self.sampling_strategy = sampling_strategy

        assert set(distributions.keys()) == set(weights_ranges.keys()), \
            "Please provide weight_ranges for all distributions"

        intersection = set(column_ranges.keys()).intersection(parameter_ranges)
        assert len(intersection) == 0, \
            'Same variables were used both as column and parameter: {}'.format(intersection)

        self.parameters_ranges = OrderedDict(parameter_ranges.copy())
        for distr_name, distr_range in self.weight_ranges.items():
            new_name = distr_name + '_weightlog'
            assert new_name not in self.parameters_ranges, \
                'whoops: name {} was booked twice'.format(new_name)
            self.parameters_ranges[new_name] = numpy.log(distr_range)

        self.parameters = OrderedDict()
        for param_name, param_range in self.parameters_ranges.items():
            self.parameters[param_name] = numpy.mean(param_range)

    def prepare_pdf(self):
        param_ids = {name: i for i, name in enumerate(self.parameters_ranges)}
        columns_ids = {name: i for i, name in enumerate(self.column_ranges)}
        volume = numpy.prod([x[1] - x[0] for _, x in self.column_ranges.items()])

        def pdf(pos_samples, neg_samples, neg_weights, weights):
            """
            Returns global pdfs and summands of pdfs
            """
            commmon_denominator = 0.
            summands = []
            for i, (distr_name, distr_function) in enumerate(self.distributions.items()):
                pos_params = {}
                neg_params = {}
                for name in inspect.getargspec(distr_function).args:
                    if name in self.parameters_ranges:
                        pos_params[name] = weights[param_ids[name]]
                        neg_params[name] = weights[param_ids[name]]
                    else:
                        pos_params[name] = pos_samples[:, columns_ids[name]]
                        neg_params[name] = neg_samples[:, columns_ids[name]]

                weight_var = T.exp(weights[param_ids[distr_name + '_weightlog']])
                f = weight_var * distr_function(**pos_params) / T.mean(neg_weights * distr_function(**neg_params))
                summands.append(f)
                commmon_denominator += weight_var
            commmon_denominator *= volume
            return sum(summands) / commmon_denominator, [f / commmon_denominator for f in summands]

        return pdf

    def get_compiled_pdf(self, n_negative_samples=100000):
        return self._prepare_compiled_pdf(n_negative_samples=n_negative_samples)[0]

    def get_compiled_summands(self, n_negative_samples=100000):
        return self._prepare_compiled_pdf(n_negative_samples=n_negative_samples)[1]

    def _prepare_compiled_pdf(self, n_negative_samples):
        """
        Returns two function: pdf and summands
        """
        neg_data, neg_weights = self.generate_negative_samples(n_negative_samples=n_negative_samples)
        data = T.matrix('data')
        pdf_function = self.prepare_pdf()
        pdf, summands = pdf_function(data, neg_data, neg_weights, list(self.parameters.values()))
        return theano.function([data], pdf), theano.function([data], summands)

    def generate_negative_samples(self, n_negative_samples, strategy='grid'):
        """ Generates samples used to compute normalization constant """
        result = numpy.zeros([n_negative_samples, len(self.column_ranges)])
        if strategy == 'random':
            for i, (column_name, column_range) in enumerate(self.column_ranges.items()):
                lower, upper = column_range
                result[:, i] = self.random_state.uniform(lower, upper, size=n_negative_samples)
        elif strategy == 'grid':
            along_axis = numpy.ceil(n_negative_samples ** (1. / len(self.column_ranges)))
            axes = []
            for column_name, column_range in self.column_ranges.items():
                lower, upper = column_range
                axes.append(numpy.linspace(lower, upper, 2 * along_axis + 1)[1::2])
            result = numpy.vstack(map(numpy.ravel, numpy.meshgrid(*axes))).T
        else:
            raise ValueError('unknown value of strategy: {}'.format(strategy))
        return result, numpy.ones(len(result))

    def compile(self,X,n_negative_samples=None):
        if n_negative_samples is None:
            n_negative_samples = 1000
	
	pos_samples = X.loc[:, self.column_ranges.keys()].values.astype(floatX)

        pos_data, neg_data = T.matrices('SigData', 'BckData')
        pos_w, neg_w, parameters = T.vectors('SigW', 'BckW', 'parameters')

	neg_samples, neg_weight = self.generate_negative_samples(n_negative_samples=n_negative_samples,
                                                                 strategy=self.sampling_strategy)

        givens = {pos_data: pos_samples, neg_data: neg_samples,  neg_w: neg_weight}

	pdf = self.prepare_pdf()
        pdfs, summands = pdf(pos_data, neg_data, neg_weights=neg_w, weights=parameters)
        result = - T.mean(pos_w * T.log(pdfs))

	self.Tfunction = theano.function([parameters,pos_w], result, givens=givens)
        self.Tderivative = theano.function([parameters,pos_w], T.grad(result, parameters), givens=givens)
	self.X=X
        

    def fit(self,sample_weight,values_init=None):
	X = self.X

        assert isinstance(X, pandas.DataFrame), 'please pass pandas.DataFrame first'
        for column_name, column_range in self.column_ranges.items():
            lower, upper = column_range
            assert numpy.all(X[column_name] >= lower) and numpy.all(X[column_name] <= upper), \
                '{} out of range'.format(column_name)

        pos_weight = check_sample_weight(X, sample_weight=sample_weight,normalize = True)
	self.Function = lambda parameters:self.Tfunction(parameters,pos_weight)
	self.Derivative = lambda parameters:self.Tderivative(parameters,pos_weight)

        lower_boundary = numpy.zeros(len(self.parameters_ranges))
        upper_boundary = numpy.zeros(len(self.parameters_ranges))
        initial_values = numpy.zeros(len(self.parameters_ranges))

        for i, (param_name, param_range) in enumerate(self.parameters_ranges.items()):
            if len(param_range) == 2:
                lower_boundary[i], upper_boundary[i] = param_range
                initial_values[i] = (lower_boundary[i] + upper_boundary[i]) / 2.
            else:
                lower_boundary[i], initial_values[i], upper_boundary[i] = param_range
                assert lower_boundary[i] <= initial_values[i] <= upper_boundary[i], \
                    'For variable {} passed initial value was outside range'.format(param_name)

	if values_init is not None:
	    assert type(values_init) is dict
            for i,param_name in enumerate(self.parameters_ranges.keys()):
                if param_name in values_init:
                    initial_values[i] = values_init[param_name]
	self.optimization_result = minimize(self.Function, initial_values, jac=self.Derivative,
                                            # hessp=self.HessianTimesP,
                                            bounds=list(self.parameters_ranges.values()))
        self.parameters = OrderedDict(zip(self.parameters_ranges, self.optimization_result.x))

    def get_params(self):
        return self.parameters.copy()

    def set_params(self, **params):
        for name, value in params.items():
            assert name in self.parameters, '{} is not valid parameter'.format(name)
            self.parameters[name] = value


class SPlot(object):
    def __init__(self, mixture_fitter):
        """
        sPlot is reweighting technique that helps reconstruct features
        that are statistically independent from variables used in fit.

        :param mixture_fitter: fitted mixture, each distribution should refer to particular class.
        :type mixture_fitter: DistributionsMixture
        """
        self.mixture_fitter = mixture_fitter

    def predict_sweights(self, X):
        """Predicting sWeights for data sample.

        :param X: pandas.DataFrame with data, should coincide with dataset used during fitting.
        :return: numpy.array of shape [n_samples, ]
        """
        assert isinstance(X, pandas.DataFrame), 'please pass pandas.DataFrame'
        summand_pdfs = self.mixture_fitter.get_compiled_summands()
        pos_samples = X.loc[:, self.mixture_fitter.column_ranges].values.astype(floatX)
        probabilities = numpy.array(summand_pdfs(pos_samples), dtype='float64').T
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        #
        initial_stats = probabilities.sum(axis=0)
        V_inv = probabilities.T.dot(probabilities)
        V = numpy.linalg.inv(V_inv)
        result = probabilities.dot(V) * initial_stats[numpy.newaxis, :]
        return pandas.DataFrame(result, columns=self.mixture_fitter.distributions.keys())
