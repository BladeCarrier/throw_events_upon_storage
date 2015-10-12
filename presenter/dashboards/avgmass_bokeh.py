import sys
sys.path.append("..")
from dashboard import Dashboard
from bokeh.charts import Histogram
from bokeh.plotting import figure  
import visualize.web_bokeh as vis_bokeh

class avgmass(Dashboard):
    def __init__(self):
        self.name = "avgmass_bokeh"
    def knit_html(self,es):
        fig = figure()
        _=vis_bokeh.plot_1d_hist("avgMass",0,70,50,es,"run*",ax=fig)
        return vis_bokeh.fig_to_html(fig)
    

dashboard = avgmass()
