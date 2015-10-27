#prototype code; view at your own risk
__doc__="demo dashboard that visualizes 1d dummy histogram"
import sys
sys.path.append("..")
from dashboard import Dashboard
from bokeh.charts import Histogram
from bokeh.plotting import figure  
from visualize.web_bokeh import fig_to_html

class some_hist_bokeh(Dashboard):
    def __init__(self):
        self.name = "Online Dashboard"
    def knit_html(self,es):
        with open("static/dashboard1/widget4.html") as fdash:
            html = fdash.read()
        return html

dashboard = some_hist_bokeh()
        
