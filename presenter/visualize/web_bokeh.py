__doc__ = "i draw histograms from the ELasticSearch terms aggregations"
from elastic.queries import get_1d_hist, get_2d_hist

from bokeh.plotting import figure

import numpy as np

def classic_histogram(xmin,xmax,xbins,counts,fig=None,
                             line_color="#033649",
                             fill_color="white",
                             ):
    """draw (on a fig, or on a new figure) a classical histogram
    output: a figure with abovementioned hist on it
    xmin,xmax - min and max values of the counted variable
    xbins - amount (integer) of bins in the histogram
    counts - array of bin counts [number_of_x_in_bin(i) for i in range(xbins)]
    fig - a figure to draw on (None means new figure)
    other: style parameters
    example usage:
        #draw hist with 50 bins with x ranging from 11 to 23
        bokeh.plotting.output_notebook()
        counts = np.histogram(yourData,range=[11.,23.],bins=50)[0] 
        deltas = np.sqrt(counts)
        fig = bokeh_whiskered_histogram(11.,23.,50,counts,deltas,-deltas)
        bokeh.plotting.show(fig)
    """

    if fig is None:
        fig = figure()

    edges = np.histogram([], range = [xmin,xmax],bins= xbins )[1]
    
    fig.quad(top=counts, bottom=0, left=edges[:-1], right=edges[1:],
            fill_color=fill_color, line_color=line_color)
    return fig

def whiskered_histogram(xmin,xmax,xbins,counts,deltas1,deltas2,fig=None,
                             point_size=10.,
                             center_color="blue",
                             whisker_breadth_factor = 0.3,#whisker cap length relative to bin width
                             vline_width = 0.3,#whisker stem
                             hline_width = 0.01,#whisker cap
                             whisker_color="black",
                             ):
    """draw (on a fig, or on a new figure) a CERN-ish whiskered histogram
    output: a figure with abovementioned hist on it
    xmin,xmax - min and max values of the counted variable
    xbins - amount (integer) of bins in the histogram
    counts - array of bin counts [number_of_x_in_bin(i) for i in range(xbins)]
    deltas1,deltas2 - lengths of (positive/negative) whiskers for each count (order invariant)
    fig - a figure to draw on (None means new figure)
    other: style parameters
    example usage:
        #draw hist with 50 bins with x ranging from 11 to 23
        bokeh.plotting.output_notebook()
        counts = np.histogram(yourData,range=[11.,23.],bins=50)[0] 
        deltas = np.sqrt(counts)
        fig = bokeh_whiskered_histogram(11.,23.,50,counts,deltas,-deltas)
        bokeh.plotting.show(fig)
    """
    if fig is None:
        fig = figure()
        
    whisker_breadth = whisker_breadth_factor * (xmax-xmin)/xbins
    
    bin_separators = np.histogram([],range=[xmin,xmax],bins=xbins)[1]
    bin_centers = np.array([0.5*(bin_separators[i]+bin_separators[i+1]) for i in range(len(bin_separators)-1)])


    # whiskers (almost-0 height rects simpler than segments)
    #vertical
    fig.segment(bin_centers, counts, bin_centers, counts+deltas1, line_width=vline_width, line_color=whisker_color)
    fig.segment(bin_centers, counts, bin_centers, counts+deltas2, line_width=vline_width, line_color=whisker_color)
    #horizontal
    fig.rect(bin_centers, counts+deltas1, whisker_breadth, hline_width, line_color=whisker_color,color="white")
    fig.rect(bin_centers, counts+deltas2, whisker_breadth, hline_width, line_color=whisker_color,color="white")
    #draw centers last above everything else
    fig.scatter(bin_centers,counts,size=point_size,color=center_color) 
    return fig

def draw_1d_hist_from_es(xname,xmin,xmax,xbins,es,index="*",ax=None,hist_drawer="whiskers"):
    """i plot the histogram of a variable xname between xmin,xmax with xbins uniform bins.
    i require es to be an elasticsearch.Elasticsearch client. 
    if hist_drawer == "whiskers", plots a CERNish whiskered histogram
    elif hist_drawer == "classic", plots a regular one
    else tries to use hist_drawer as a function(xmin,xmax,xbins,counts,fig=<bokeh figure>) -> figure"""
        
    x,c = get_1d_hist(xname,xmin,xmax,xbins,es,index=index)
    
    if hist_drawer == "whiskers":
        deltas = np.sqrt(c)
        #use whiskered-specific interface
        return whiskered_histogram(xmin,xmax,xbins,c,deltas,-deltas,fig=ax)
    elif hist_drawer == "classic":
        hist_drawer = classic_histogram
        
    return hist_drawer(xmin,xmax,xbins,c,fig=ax)
     
from bokeh.models import DataRange1d as brange

def draw_2d_hist_from_es(xname,xmin,xmax,xbins,
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

