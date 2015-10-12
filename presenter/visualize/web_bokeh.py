__doc__ = "i draw histograms from the ELasticSearch terms aggregations"
from elastic.queries import get_1d_hist, get_2d_hist

from bokeh.plotting import figure

import numpy as np
def plot_1d_hist(xname,xmin,xmax,xbins,es,index="*",ax=None):
    """i plot the histogram of a variable xname between xmin,xmax with xbins uniform bins.
    i require es to be an elasticsearch.Elasticsearch client. """
    if ax is None:
        ax = figure()
    x,c = get_1d_hist(xname,xmin,xmax,xbins,es,index=index)
    hist,edges = np.histogram(x,
                range = [xmin,xmax],bins= xbins ,
                weights=c)
    return ax.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
     fill_color="#036564", line_color="#033649",\
    )
     
from bokeh.models import DataRange1d as brange

def plot_2d_hist(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index="*",ax = None):
    """i plot the 2d histogram (heatmap) of a variables xname and yname 
    between [xmin,xmax],[ymin,ymax] with [xbins,ybins] uniform bins respectively.
    i require es to be an elasticsearch.Elasticsearch client"""
    if ax is None:
        ax = figure()
    
    x,y,c = get_2d_hist(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index=index)
    bin_w = (xmax-xmin)/float(xbins)
    bin_h = (ymax-ymin)/float(ybins)
    x = map(lambda x_i: int(x_i/bin_w), x) 
    y = map(lambda y_i: int(y_i/bin_h), y) 

    
    
    ax.x_range= brange(start=xmin,end=xmax)
    ax.y_range= brange(start=xmax,end=xmin)
    img = np.zeros([xbins,ybins])
    img[x,y] = c
    return ax.image(image=[img], x=[xmin], y=[ymax], 
         dw=[xmax-xmin], dh=[ymax-ymin], palette='RdYlBu11')
    

from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.plotting import figure
from bokeh.resources import INLINE

def fig_to_html(fig,title="figure"):
    """convert bokeh figure into html string the easy way"""
    doc = Document()
    doc.add(fig)
    return file_html(doc,INLINE,title)
