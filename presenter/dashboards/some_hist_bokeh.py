import sys
sys.path.append("..")
from dashboard import Dashboard
from bokeh.charts import Histogram
from bokeh.plotting import figure  
from visualize.web_bokeh import fig_to_html

class some_hist_bokeh(Dashboard):
    def __init__(self):
        self.name = "some_hist_bokeh"
    def knit_html(self,es):
        hist = Histogram([1,2,3])
        return fig_to_html(hist)

dashboard = some_hist_bokeh()
        
