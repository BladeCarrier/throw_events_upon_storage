from flask import Flask, render_template, json, request
import numpy as np


import matplotlib
import json
import random

matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()

from threading import Lock
lock = Lock()
import datetime
import mpld3
from mpld3 import plugins


#ElasticSearch part
import elasticsearch
import visualize
es = elasticsearch.Elasticsearch(["localhost:9200"])
#/elasticSearch



# Setting up matplotlib sytles using BMH
s = json.load(open("./static/bmh_matplotlibrc.json"))
matplotlib.rcParams.update(s)

def draw_layout(dashboard_name):
    """Returns html equivalent of matplotlib figure

    Parameters
    ----------
    fig_type: string, type of figure
            one of following:
                    * line
                    * bar

    Returns
    --------
    d3 representation of figure
    """

    with lock:
	print dashboard_name
	if dashboard_name == "dummy hist":
            fig, ax = plt.subplots()
	    ax.hist([1,2,3])
        elif dashboard_name == "muonHits":
            fig, axes = plt.subplots(3,2,figsize = [10,15])
	    
            _=visualize.plot_1d_hist("avgMass",0,70,50,es,"run*",ax=axes[0,0])
    	    axes[0,0].set_xlabel("avgMass")

            _=visualize.plot_1d_hist("muonHits",0,70,50,es,"run*",ax=axes[1,1])
    	    axes[1,1].set_xlabel("avgTODO")

            xmin,xmax = 0,65
            xbins = 20
            xname = "hcalEnergy"
            ymin,ymax = 0,65
            ybins = 20
            yname = "muonHits"
            HistInfo=visualize.plot_2d_hist(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=axes[2,1])
            axes[2,1].set_xlabel(xname)
	    axes[2,1].set_ylabel(yname)

            xmin,xmax = 0,65
            xbins = 20
            xname = "avgMass"
            ymin,ymax = 0,65
            ybins = 20
            yname = "muonHits"
            HistInfo=visualize.plot_2d_hist(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=axes[0,1])
            axes[0,1].set_xlabel(xname)
	    axes[0,1].set_ylabel(yname)

	    axes[1,0].hist([1,2,3,4,5])
	    axes[1,0].set_ylabel("epic histogram of fates")
	    
            axes[2,0].scatter(np.random.normal(size=50),np.random.normal(size=50))
            axes[2,0].set_xlabel("scatterized Lena")


        elif dashboard_name == "some heatmap":
            fig, ax = plt.subplots()
            xmin,xmax = 0,65
            xbins = 20
            xname = "hcalEnergy"
            ymin,ymax = 0,65
            ybins = 20
            yname = "muonHits"
            HistInfo=visualize.plot_2d_hist(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=ax)
            #plt.colorbar(HistInfo[3])
            plt.xlabel(xname)
	    plt.ylabel(yname)

    
    return mpld3.fig_to_html(fig)

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    data = json.loads(request.data)
    return draw_layout(data["dashboard"])


if __name__ == '__main__':
    app.run(debug=False, host='localhost')
