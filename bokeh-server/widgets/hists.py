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

from base import _BaseWidget

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
