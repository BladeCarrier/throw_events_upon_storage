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
import visualize_mpl as vis_mpl
import visualize_bokeh as vis_bokeh
es = elasticsearch.Elasticsearch(["localhost:9200"])
#/elasticSearch
#bokeh
from bokeh.charts import Histogram
from bokeh.plotting import figure  
#/bokeh



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
            
	    hist = Histogram([1,2,3])
	    html = vis_bokeh.fig_to_html(hist)
	elif dashboard_name == "bokeh_avgmass":
	              	
	    fig = figure()
	    _=vis_bokeh.plot_1d_hist("avgMass",0,70,50,es,"run*",ax=fig)
	    html = vis_bokeh.fig_to_html(fig)
	    
	elif dashboard_name == "dashboard_bokeh":
	    from bokeh.io import vplot ,hplot
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
	    
	    html = vis_bokeh.fig_to_html(fig_grid)

	    
	    
        elif dashboard_name == "dashboard_mpl":
            fig, axes = plt.subplots(3,2,figsize = [10,15])
	    
            _=vis_mpl.plot_1d_hist("avgMass",0,70,50,es,"run*",ax=axes[0,0])
    	    axes[0,0].set_xlabel("avgMass")

            _=vis_mpl.plot_1d_hist("muonHits",0,70,50,es,"run*",ax=axes[1,1])
    	    axes[1,1].set_xlabel("avgTODO")

            xmin,xmax = 0,65
            xbins = 20
            xname = "hcalEnergy"
            ymin,ymax = 0,65
            ybins = 20
            yname = "muonHits"
            HistInfo=vis_mpl.plot_2d_hist(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=axes[2,1])
            axes[2,1].set_xlabel(xname)
	    axes[2,1].set_ylabel(yname)

            xmin,xmax = 0,65
            xbins = 20
            xname = "avgMass"
            ymin,ymax = 0,65
            ybins = 20
            yname = "muonHits"
            HistInfo=vis_mpl.plot_2d_hist(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=axes[0,1])
            axes[0,1].set_xlabel(xname)
	    axes[0,1].set_ylabel(yname)

	    axes[1,0].hist([1,2,3,4,5])
	    axes[1,0].set_ylabel("epic histogram of fates")
	    
            axes[2,0].scatter(np.random.normal(size=50),np.random.normal(size=50))
            axes[2,0].set_xlabel("scatterized Lena")
            html = mpld3.fig_to_html(fig)


        elif dashboard_name == "some heatmap":
            fig, ax = plt.subplots()
            xmin,xmax = 0,65
            xbins = 20
            xname = "hcalEnergy"
            ymin,ymax = 0,65
            ybins = 20
            yname = "muonHits"
            HistInfo=vis_mpl.plot_2d_hist(xname,xmin,xmax,xbins,yname,ymin,ymax,ybins,es,index="run*",ax=ax)
            #plt.colorbar(HistInfo[3])
            plt.xlabel(xname)
	    plt.ylabel(yname)
            html = mpld3.fig_to_html(fig)
    	    print html
    return html

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    data = json.loads(request.data)
    return draw_layout(data["dashboard"])


if __name__ == '__main__':
    app.run(debug=True, host='localhost')
