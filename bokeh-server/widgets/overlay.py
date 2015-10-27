__doc__="""this module contains several overlays to the histogram widgets from widgets.hists"""

import visualize.web_bokeh as vis_bokeh
import numpy as np
from elastic.queries import get_1d_hist
from bokeh.plotting import figure

from base import _BaseWidget

class ReferenceOverlay(_BaseWidget):
    def __init__(self,histogram_widget,reference_pdf,n_pts = 1000):
        """a widget that draws a reference pdf above the base histogram_widget
        histogram_widget must be a 1D histogram widget implementing _BaseHistWidget
        reference_pdf must be callable(x_array)->proba_array"""
        self.base = histogram_widget
        self.n_pts = n_pts
        
        self.fig = self.base.fig #assuming base is initialized
        
        base = self.base
        
        
        #average share of events per bin, used to compute pdf height
        self.bin_density = (base.xmax - base.xmin)/float(base.xbins)
        
        self.pdf = reference_pdf
        
        self.pts_x =pts_x= np.arange(n_pts,dtype='float')/n_pts*(base.xmax-base.xmin) + base.xmin
        self.pts_y_per_evt = self.pdf(pts_x)*self.bin_density
        
        #plot the pdfs
        self.draw_pdf_lines(self.fig,n_pts)
        
    
    def draw_pdf_lines(self,fig,n_pts = 1000):
        """draws the pdf lines"""        
        base = self.base
        counts = base.binc
        
        pts_x = self.pts_x
        pts_y = self.pts_y_per_evt*self.bin_density*np.sum(counts)
        
        
        fig.line(pts_x, pts_y, legend="Reference", line_width=2,color = 'red',name ="ref")
        return fig

    def get_updates(self):
        
        
        #get base histogram updates, ALSO reattain (binx,binc)
        base_updates = self.base.get_updates()
        
        base = self.base
        counts = base.binc
        
        pts_y = self.pts_y_per_evt*np.sum(counts)
        
        ref_ds = self.fig.select(dict(name="ref"))[0].data_source
        ref_ds.data["y"] = pts_y

        overlay_updates = [ref_ds]
        
        
        return base_updates + overlay_updates


class MLFitOverlayWidget(_BaseWidget):
    def __init__(self,histogram_widget,model,model_initial_values = {},n_pts = 1000):
        """a widget that fits and draws a distribution mixture over the histogram.
        histogram_widget must be a 1D histogram widget implementing _BaseHistWidget
        model has to be a COMPILED analyze.distfit model"""
        self.base = histogram_widget
        self.model = model
        self.model_init = model_initial_values
        
        base = self.base
        xmin, xmax,xbins = base.xmin, base.xmax, base.xbins   
        
        self.n_pts = n_pts
        self.pts_x = np.arange(n_pts,dtype='float')/n_pts*(xmax-xmin) + xmin
        
        self.fig = self.base.fig #assuming base is initialized
        
        #plot the pdfs
        self.draw_pdf_lines(self.fig,n_pts)
        
        
    def call_pdf(self,pdf,x,parameters):
        """utilizes parameter dict to get optimal pdf at x vector"""
        args = pdf.func_code.co_varnames
        kwargs={arg:parameters.get(arg,x) for arg in args if arg != 't'}
        return pdf(**kwargs).eval()
    def get_mlfit_pdfs(self):
        """computes optimal pdf parameters. utilizes self.binx and self.binc set up by get_hist_data.
        returns: (signal pdf, background pdf, dict of parameters)"""
        #get maxlikeihood fit
        x,c = self.base.binx,self.base.binc
        
        
        model = self.model
        model.fit(sample_weight=c,values_init=self.model_init)

        parameters = model.parameters
        self.model_init = parameters
        
        pdf_signal = model.distributions['sig']
        pdf_background = model.distributions['bck']
        return pdf_signal,pdf_background, parameters
    
    def get_pdf_lines(self,n_pts=1000):
        """returns the chart lines: (x,pdf_signal,pdf_background)"""
        
        pdf_signal,pdf_background,parameters = self.get_mlfit_pdfs()
        base= self.base
        xmin, xmax,xbins = base.xmin, base.xmax, base.xbins        

        #get pdf points
        pts_x = self.pts_x
        
        #compute pdf weights
        w_sig,w_bkg =np.exp(parameters['sig_weightlog']),np.exp(parameters['bck_weightlog'])
        w_sum = w_sig+w_bkg
        w_sig,w_bkg = w_sig/w_sum,w_bkg/w_sum
        n_events = np.sum(self.base.binc)
        norm = n_events*(xmax-xmin)/xbins

        #get pdfs themselves
        p_signal = self.call_pdf(pdf_signal,pts_x,parameters)*w_sig*norm
        p_background = self.call_pdf(pdf_background,pts_x,parameters)*w_bkg*norm
        return pts_x, p_signal, p_background
    
    def draw_pdf_lines(self,fig,n_pts = 1000):
        """draws the pdf lines"""        
        pts_x,p_signal,p_background = self.get_pdf_lines(n_pts)
        p_together = p_signal + p_background        
        
        fig.line(pts_x, p_background, legend="Background", line_width=2,color = 'red',name ="pdf_bck")
        fig.line(pts_x, p_signal, legend="Signal", line_width=2,color='blue',name="pdf_sig")
        fig.line(pts_x, p_together, legend="Total pdf", line_width=2,color='green',name="pdf_sum")
        return fig

    def get_updates(self):
        
        
        #get base histogram updates, ALSO reattain (binx,binc)
        base_updates = self.base.get_updates()
        
        #get new optimal pdfs; implicitly assumes that binx,binc are updated from the ElasticSearch
        pts_x,p_signal,p_background = self.get_pdf_lines(self.n_pts)
        p_together = p_signal + p_background 
        
        
        bck_ds = self.fig.select(dict(name="pdf_bck"))[0].data_source
        bck_ds.data["y"] = p_background
        sig_ds = self.fig.select(dict(name="pdf_sig"))[0].data_source
        sig_ds.data["y"] = p_signal
        sum_ds = self.fig.select(dict(name="pdf_sum"))[0].data_source
        sum_ds.data["y"] = p_together
        overlay_updates = [sum_ds,bck_ds,sig_ds]
        
        
        return base_updates + overlay_updates