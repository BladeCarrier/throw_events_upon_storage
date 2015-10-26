__doc__="""this module contains several Bokeh widgets that automagically update their content at wherever they are displayed.
To utilize the automatic updates, one has to call the widget.get_updates and push it to the current bokeh session.
Example usage code:
#create widgets for hist and heatmap
hist2 = WhiskeredHistWidget("muonHits",0,100,30,es,
                   fig = figure(plot_width=600, plot_height=600))
hist3 = HeatmapWidget("avgMass",0,40,50,
                      "muonHits",0,100,50,
                      es,fig = figure(plot_width=600, plot_height=600))

#create a widget for histogram with mlfit overlay
import analysis.distfit as distfit
import pandas as pd
xname,xmin,xmax,xbins = "invariantMass",0,10,50


bin_separators = np.histogram([],bins=xbins, range=[xmin,xmax])[1]
bin_centers = np.array([0.5*(bin_separators[i]+bin_separators[i+1]) for i in range(len(bin_separators)-1)])
bins = pd.DataFrame({"x":bin_centers})


mix_model = distfit.DistributionsMixture(
    distributions={'sig': distfit.gauss, 'bck': distfit.exponential},
    weights_ranges={'sig': [1.,10.], 'bck': [1.,10.]},
    parameter_ranges={'mean': [xmin ,xmax], 'sigma': [0., xmax-xmin], 'slope': [0, 15.]},
    column_ranges={'x': [xmin, xmax]},
    sampling_strategy='grid',
)
mix_model.compile(bins,1000) #takes several seconds

hist1_base = WhiskeredHistWidget(xname,xmin,xmax,xbins,es,
                   fig = figure(plot_width=600, plot_height=600))
hist1 = MLFitOverlayWidget(hist1_base,mix_model,n_pts=100)


#publish the plots to the bokeh server
client = MY_BOKEH_SERVER_SESSION #assuming you have one

hists=[hist1,hist2,hist3]

plot = hplot(*[hist.fig for hist in hists[:3]])
client.show(plot)
client.publish()


#start updating the plots
while True:
    for hist in hists:
        upd_sources = hist.get_updates()
        client.store_objects(*upd_sources)
    time.sleep(0.5);

"""

import visualize.web_bokeh as vis_bokeh
import numpy as np
from elastic.queries import get_1d_hist
from bokeh.plotting import figure

class _BaseWidget(object):
    """widget interface you gotta implement to create your own widget"""
    def __init__(self):
        """initialize the widget"""
        pass
    def get_updates(self):
        """return the list of bokeh data_sources to be updated on the bokeh server"""
        return []
class _BaseHistWidget(_BaseWidget):
    """abstract base class for histogram widgets"""
    def __init__(self,xname,xmin,xmax,xbins,es,fig=None,index="run*"):
        self.xname,self.xmin,self.xmax,self.xbins=xname,xmin,xmax,xbins
        self.es = es
        self.index = index
        self.fig=self.get_hist(fig)
    def get_hist(self,fig):
        """returns a figure containing the histogram"""
        if fig is None:
            fig = figure()

        return fig
    def get_hist_data(self):
        """returns the tuple of arrays (bin_centers,bin_counts),also saves them as self.binx and self.binc"""
        es = self.es
        index = self.index
        xname,xmin,xmax,xbins = self.xname,self.xmin,self.xmax,self.xbins
        
        x,c = get_1d_hist(xname,xmin,xmax,xbins,es,index = index)
        self.binx, self.binc = x,c
        return x,c
    def get_updates(self):
        """returns a list of bokeh data_source objects"""
        return []

class ClassicHistWidget(_BaseHistWidget):
    """classical histogram with bars"""
    def get_hist(self,fig):
        x,c = self.get_hist_data()
        return vis_bokeh.classic_histogram(self.xmin,self.xmax,self.xbins,c,fig=fig)
    def get_updates(self):
        """returns a list of bokeh data_source objects"""
        x,c = self.get_hist_data()       
        quads_renderer = self.fig.select(dict(name="quads"))[0]
        quads_ds = quads_renderer.data_source
        quads_ds.data["top"] = c
        return [quads_ds]
    
class WhiskeredHistWidget(_BaseHistWidget):
    """CERNish histogram with whiskers"""
    def get_hist(self,fig):
        x,c = self.get_hist_data()
        deltas = np.sqrt(c)
        return vis_bokeh.whiskered_histogram(self.xmin,self.xmax,self.xbins,
                                                 c,deltas,-deltas,
                                                 fig=fig)
    def get_updates(self):
        """returns a list of bokeh data_source objects"""
        x,c = self.get_hist_data()    
        deltas = np.sqrt(c)

        centers_ds = self.fig.select(dict(name="centers"))[0].data_source
        centers_ds.data["y"] = c
        
        stem1_ds = self.fig.select(dict(name="stems1"))[0].data_source
        stem1_ds.data["y0"] = c
        stem1_ds.data["y1"] = c+deltas
        
        stem2_ds = self.fig.select(dict(name="stems2"))[0].data_source
        stem2_ds.data["y0"] = c
        stem2_ds.data["y1"] = c-deltas
        
        caps1_ds = self.fig.select(dict(name="caps1"))[0].data_source
        caps1_ds.data["y"] = c+deltas
        
        caps2_ds = self.fig.select(dict(name="caps2"))[0].data_source
        caps2_ds.data["y"] = c-deltas
        
        return [centers_ds,stem1_ds,stem2_ds,caps1_ds,caps2_ds]


class MLFitOverlayWidget(_BaseWidget):
    def __init__(self,histogram_widget,model,model_initial_values = {},n_pts = 1000):
        """a widget that fits and draws a distribution mixture over the histogram.
        histogram_widget must be a 1D histogram widget implementing _BaseHistWidget
        model has to be a COMPILED analyze.distfit model"""
        self.base = histogram_widget
        self.model = model
        self.model_init = model_initial_values
        self.n_pts = n_pts

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
        pdf_signal = model.distributions['sig']
        pdf_background = model.distributions['bck']
        return pdf_signal,pdf_background, parameters
    
    def get_pdf_lines(self,n_pts=1000):
        """returns the chart lines: (x,pdf_signal,pdf_background)"""
        
        pdf_signal,pdf_background,parameters = self.get_mlfit_pdfs()
        base= self.base
        xmin, xmax,xbins = base.xmin, base.xmax, base.xbins        

        #get pdf points
        pts_x = np.arange(n_pts,dtype='float')/n_pts*(xmax-xmin) + xmin
        
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
        
        
import matplotlib as mpl
import matplotlib.cm as cm
from elastic.queries import get_2d_hist

class HeatmapWidget(_BaseWidget):
    def __init__(self,xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index="run*",fig=None,cmap = cm.RdYlBu):
        if fig is None:
            fig = figure()
        
        self.es = es
        self.index = index

        self.xname,self.xmin,self.xmax,self.xbins=xname,xmin,xmax,xbins
        self.yname,self.ymin,self.ymax,self.ybins=yname,ymin,ymax,ybins

        
        #get first histogram 
        x,y,c = get_2d_hist(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index=index)
        x,y,c = map(np.array,[x,y,c])
        
        self.cmap = cmap
        self.fig = vis_bokeh.classic_heatmap(x,y,c,xmin,xmax,xbins,
                                 ymin,ymax,ybins,fig=fig,cmap = cmap)
        

    def get_updates(self):
        es = self.es
        index = self.index
        xname,xmin,xmax,xbins = self.xname,self.xmin,self.xmax,self.xbins
        yname,ymin,ymax,ybins = self.yname,self.ymin,self.xmax,self.xbins
        
        x,y,c = get_2d_hist(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index=index)
        x,y,c = map(np.array,[x,y,c])
        

        #compute color codes using the given cmap
        cmap = self.cmap
        norm = mpl.colors.Normalize(vmin=0, vmax=np.percentile(c,90),clip=True)
        mapper = cm.ScalarMappable(norm=norm,cmap=cmap)

        colors_int = (mapper.to_rgba(c)*256).astype(int)

        ascode = lambda (r,g,b,a):"#{:02x}{:02x}{:02x}".format(r,g,b)
        color_codes = np.apply_along_axis(ascode,-1,colors_int)

        quads_renderer = self.fig.select(dict(name="quads"))[0]
        quads_ds = quads_renderer.data_source
        quads_ds.data["fill_color"] = color_codes
	quads_ds.data["line_color"] = color_codes
        
        return[quads_ds]
