# -*- coding: utf-8 -*-
__doc__="demo dashboard that visualizes 1d histogram aggregated from ElasticSearch data"



import sys
import json
from bokeh.charts import Histogram
from bokeh.plotting import figure  
import visualize.web_bokeh as vis_bokeh
import elasticsearch

from common import HTMLWidget

import time


es = elasticsearch.Elasticsearch(["localhost:9200"])

class BokehHistWidget(HTMLWidget):
    def __init__(self):
        """called once widget is refreshed"""
	pass
    def get_value(self):
        fig = figure()
        _=vis_bokeh.draw_1d_hist_from_es("avgMass",0,40,50,es,"run*",ax=fig)
        fig.xaxis.axis_label = time.strftime("%H:%M:%S")
        fig_html = vis_bokeh.fig_to_html(fig)
        return fig_html




NAME = "HistWidget"

def get_widget():
    return BokehHistWidget

from django.conf.urls import url
def get_urls():
    return [url(r'^bokeh_to_html/', make_html, name='bokeh_to_html')]


from django.shortcuts import HttpResponse
def make_html(request):
    """i knit a bokeh html if asked from AJAX"""
    fig = figure()
    _=vis_bokeh.draw_1d_hist_from_es("avgMass",0,40,50,es,"run*",ax=fig)
    fig.xaxis.axis_label = time.strftime("%H:%M:%S")
    fig_html = vis_bokeh.fig_to_html(fig)
    return HttpResponse(fig_html)	

