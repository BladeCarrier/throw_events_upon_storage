#prototype code; view at your own risk
__doc__="demo dashboard that visualizes a mixture of 1d and 2d histograms aggregated from ElasticSearch data"
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


class MplDashboard(Dashboard):
    def __init__(self):
        self.name = "dashboard_mpl"
    def knit_html(self,es):
        fig, axes = plt.subplots(3,2,figsize = [10,15])

        _=vis_mpl.draw_1d_hist_from_es("avgMass",0,70,50,es,"run*",ax=axes[0,0])
        axes[0,0].set_xlabel("avgMass")

        _=vis_mpl.draw_1d_hist_from_es("muonHits",0,70,50,es,"run*",ax=axes[1,1])
        axes[1,1].set_xlabel("avgTODO")

        xmin,xmax = 0,65
        xbins = 20
        xname = "hcalEnergy"
        ymin,ymax = 0,65
        ybins = 20
        yname = "muonHits"
        HistInfo=vis_mpl.draw_2d_hist_from_es(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=axes[2,1])
        axes[2,1].set_xlabel(xname)
        axes[2,1].set_ylabel(yname)

        xmin,xmax = 0,65
        xbins = 20
        xname = "avgMass"
        ymin,ymax = 0,65
        ybins = 20
        yname = "muonHits"
        HistInfo=vis_mpl.draw_2d_hist_from_es(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=axes[0,1])
        axes[0,1].set_xlabel(xname)
        axes[0,1].set_ylabel(yname)

        axes[1,0].hist([1,2,3,4,5])
        axes[1,0].set_ylabel("epic histogram of fates")

        axes[2,0].scatter(np.random.normal(size=50),np.random.normal(size=50))
        axes[2,0].set_xlabel("scatterized Lena")
        return mpld3.fig_to_html(fig)


dashboard = MplDashboard()

        
