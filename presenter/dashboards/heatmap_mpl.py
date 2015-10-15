#prototype code; view at your own risk
__doc__="demo dashboard that visualizes 2d histogram aggregated from ElasticSearch data"
import json
from dashboard import Dashboard
import mpld3
from mpld3 import plugins
import numpy as np

import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')
# Setting up matplotlib sytles using BMH
s = json.load(open("./static/bmh_matplotlibrc.json"))
matplotlib.rcParams.update(s)
plt.ioff()

import visualize.web_mpl as vis_mpl


class HeatmapDashboard(Dashboard):
    def __init__(self):
        self.name = "heatmap_mpl"
    def knit_html(self,es):
        fig, ax = plt.subplots()
        xmin,xmax = 0,65
        xbins = 20
        xname = "hcalEnergy"
        ymin,ymax = 0,65
        ybins = 20
        yname = "muonHits"
        HistInfo=vis_mpl.draw_2d_hist_from_es(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=ax)
        #plt.colorbar(HistInfo[3])
        plt.xlabel(xname)
        plt.ylabel(yname)
        html = mpld3.fig_to_html(fig)
        return html


dashboard = HeatmapDashboard()

        
