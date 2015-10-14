#prototype code; view at your own risk
__doc__="demo dashboard that visualizes several interactive 1d histograms aggregated from ElasticSearch data"
import sys
sys.path.append("..")
from dashboard import Dashboard
from bokeh.charts import Histogram
from bokeh.plotting import figure  
import visualize.web_bokeh as vis_bokeh
from bokeh.io import vplot ,hplot

class BokehDashboard(Dashboard):
    def __init__(self):
        self.name = "dashboard_bokeh"
    def knit_html(self,es):
        #col1
        fig1 = figure(width=250,height=250)
        _=vis_bokeh.plot_1d_hist("dummy1",0,35,30,es,"run*",ax=fig1)

        fig2=figure(width=250,height=250)
        xmin,xmax = 0,65
        xbins = 20
        xname = "hcalEnergy"
        ymin,ymax = 0,65
        ybins = 20
        yname = "muonHits"
        _=vis_bokeh.plot_2d_hist(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=fig2)
        fig_column1 = vplot(fig1,fig2)

        #col2
        fig3 = figure(width=250,height=250)
        _=vis_bokeh.plot_1d_hist("dummy23",0,100,30,es,"run*",ax=fig3)
        fig4 = figure(width=250,height=250)
        _=vis_bokeh.plot_1d_hist("dummy45",0,40,30,es,"run*",ax=fig4)
        fig_column2 = vplot(fig3,fig4)

        fig_grid = hplot(fig_column1,fig_column2)
        
        return vis_bokeh.fig_to_html(fig_grid)


dashboard = BokehDashboard()

        
