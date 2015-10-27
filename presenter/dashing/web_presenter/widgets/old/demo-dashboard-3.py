#prototype code; view at your own risk
__doc__="demo dashboard that visualizes 1d histograms aggregated from ElasticSearch data and fits gaussian+uniform distribution mixture to them"
import sys
sys.path.append("..")
from dashboard import Dashboard
from bokeh.charts import Histogram
from bokeh.plotting import figure  
import analysis.distfit as distfit
import visualize.web_bokeh as vis_bokeh
import numpy as np
import scipy.stats as st
import pandas as pd
from bokeh.io import vplot ,hplot



from collections import namedtuple
Histo = namedtuple("Histo",["name","xmin","xmax","xbins"])

class BokehGridWithMixtures(Dashboard):
    def __init__(self):
        self.name = "Demo dashboard 3"
        
        self.hists = [
            [Histo("dkpipi", 1820.,1920.,50),Histo("dskkpi", 1920.,2020.,50)],
            [Histo("lambdac", 2240.,2330.,50),Histo("phi", 1000.,1040.,50)]
        ]
        
        self.models = []
        for row in self.hists:
            self.models.append(
                        [self.get_model(hist.xmin,hist.xmax,hist.xbins) for hist in row]
                )
                
        
        
            
    def get_model(self,xmin,xmax,xbins,n_neg_samples=1000):
        #prepare hist in np
        bin_separators = np.histogram([],bins=xbins, range=[xmin,xmax])[1]
        bin_centers = np.array([0.5*(bin_separators[i]+bin_separators[i+1]) for i in range(len(bin_separators)-1)])
        bins = pd.DataFrame({"x":bin_centers})
        
        #precompile hep_ml mixture model
        
        #here dist_background is a bounded gamma
        dist_background = lambda x: distfit.uniform(x,xmin,xmax)
        mix = distfit.DistributionsMixture(
            distributions={'sig': distfit.gauss, 'bck': dist_background},
            weights_ranges={'sig': [1.,10.], 'bck': [1.,10.]},
            parameter_ranges={'mean': [xmin ,xmax], 'sigma': [0.,xmax-xmin],},
            column_ranges={'x': [xmin, xmax]},
            sampling_strategy='grid',
        )
        
        mix.compile(bins,n_neg_samples) #takes several seconds
        return mix

    def make_figure(self,hist,model,es,index="run*"):
        xname,xmin,xmax,xbins = hist.name,hist.xmin,hist.xmax,hist.xbins        
        
        x,counts = vis_bokeh.get_1d_hist(xname,xmin,xmax,xbins,es,index=index)
        
        deltas = np.sqrt(counts)
        
        fig=vis_bokeh.whiskered_histogram(xmin,xmax,xbins,counts,deltas,-deltas)
        
        #fit params
        model.fit(sample_weight=counts,values_init={'sigma':1.})
        parameters = model.parameters
        w_sig,w_bkg =np.exp(parameters['sig_weightlog']),np.exp(parameters['bck_weightlog'])
        w_sum = w_sig+w_bkg
        w_sig,w_bkg = w_sig/w_sum,w_bkg/w_sum

        n_events = np.sum(counts)
        norm = n_events*(xmax-xmin)/xbins
        
        #plot lines
        
        #residual = np.exp(-parameters['slope']*(xmax-xmin))
        #expo = lambda x_arr:st.expon(xmin,1./parameters['slope']).pdf(x_arr)*w_bkg*norm /(1.-residual)
        uni = lambda x_arr: np.repeat(1./(xmax-xmin),len(x_arr))*w_bkg*norm
        gauss = lambda x_arr:st.norm(parameters['mean'],parameters['sigma']).pdf(x_arr)*w_sig*norm
        pdf_x = np.arange(1000,dtype='float')/1000.*(xmax-xmin) + xmin
        
        sig = gauss(pdf_x)
        bkg = uni(pdf_x)
        upperLimit = np.max(counts)*1.1 # for exponential distribution peak
        bkg[bkg > upperLimit] = upperLimit

        
        
        
        fig.line(pdf_x, sig, legend="Signal", line_width=2,color='blue')
        fig.line(pdf_x, bkg, legend="Background", line_width=2,color = 'red')
        fig.line(pdf_x, sig+bkg, legend="Sum", line_width=2,color='green')

        return fig
    def knit_html(self,es):
        
        figs = []
        for i in range(len(self.hists)):
            figs.append(
                [self.make_figure(hist,model,es,"run*") for hist,model in zip(self.hists[i],self.models[i])]
                )
        hrows = [hplot(*row) for row in figs]
        grid = vplot(*hrows)
            
            
            
        
        return vis_bokeh.fig_to_html(grid)
    

dashboard = BokehGridWithMixtures()
