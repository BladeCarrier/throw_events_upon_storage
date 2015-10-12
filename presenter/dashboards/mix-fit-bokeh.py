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


class invmass(Dashboard):
    def __init__(self):
        self.name = "invmass_bokeh"
        xmin,xmax,xbins = 0,10,50

        bin_separators = np.histogram([],bins=xbins, range=[xmin,xmax])[1]
        bin_centers = np.array([0.5*(bin_separators[i]+bin_separators[i+1]) for i in range(len(bin_separators)-1)])
        bins = pd.DataFrame({"x":bin_centers})
        
        mix = distfit.DistributionsMixture(
            distributions={'sig': distfit.gauss, 'bck': distfit.exponential},
            weights_ranges={'sig': [1.,10.], 'bck': [1.,10.]},
            parameter_ranges={'mean': [xmin ,xmax], 'sigma': [0., xmax-xmin], 'slope': [0, 15.]},
            column_ranges={'x': [xmin, xmax]},
            sampling_strategy='grid',
        )
        mix.compile(bins,1000) #takes several seconds
        self.model = mix


    def knit_html(self,es):
        fig = figure()
        
        xname = "invariantMass"
        xmin,xmax,xbins = 0,10,50
        index = "run*"
        
        x,c = vis_bokeh.get_1d_hist(xname,xmin,xmax,xbins,es,index=index)
        counts,edges = np.histogram(x,
                range = [xmin,xmax],bins= xbins ,
                weights=c)
        
        #draw histogram bins
        fig.quad(top=counts, bottom=0, left=edges[:-1], right=edges[1:],
                         fill_color="#036564", line_color="#033649",\
                        )
        
        #fit params
        model = self.model
        model.fit(sample_weight=counts)#,values_init={'sig_weightlog':np.log(0.4),'bck_weightlog':np.log(0.6)})
        parameters = model.parameters
        w_sig,w_bkg =np.exp(parameters['sig_weightlog']),np.exp(parameters['bck_weightlog'])
        w_sum = w_sig+w_bkg
        w_sig,w_bkg = w_sig/w_sum,w_bkg/w_sum
        n_events = np.sum(counts)/10.
        
        #plot lines
        expo = lambda x_arr:st.expon(0,1./parameters['slope']).pdf(x_arr)*w_bkg*n_events
        gauss = lambda x_arr:st.norm(parameters['mean'],parameters['sigma']).pdf(x_arr)*w_sig*n_events
        pdf_x = np.arange(1000,dtype='float')/1000.*(xmax-xmin) + xmin
        
        fig.line(pdf_x, expo(pdf_x), legend="Background", line_width=2,color = 'red')
        fig.line(pdf_x, gauss(pdf_x), legend="Signal", line_width=2,color='blue')
        fig.line(pdf_x, gauss(pdf_x)+gauss(pdf_x), legend="Sum", line_width=2,color='green')

        
        return vis_bokeh.fig_to_html(fig)
    

dashboard = invmass()
