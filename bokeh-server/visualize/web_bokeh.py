__doc__ = "i draw histograms from the ELasticSearch terms aggregations"
from elastic.queries import get_1d_hist, get_2d_hist

from bokeh.plotting import figure

import numpy as np

def classic_histogram(xmin,xmax,xbins,counts,fig=None,
                             line_color="#033649",
                             fill_color="white",
                             name_quads="quads"
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
            fill_color=fill_color, line_color=line_color,name=name_quads)
    return fig

def whiskered_histogram(xmin,xmax,xbins,counts,deltas1,deltas2,fig=None,
                             point_size=10.,
                             center_color="blue",
                             whisker_breadth_factor = 0.3,#whisker cap length relative to bin width
                             vline_width = 0.3,#whisker stem
                             hline_width = 0.01,#whisker cap
                             whisker_color="black",
                             name_centers="centers",
                             name_whisker_stems1="stems1",
                             name_whisker_stems2="stems2",
                             name_whisker_caps1="caps1",
                             name_whisker_caps2="caps2",
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
    fig.segment(bin_centers, counts, bin_centers, counts+deltas1, line_width=vline_width, line_color=whisker_color,name=name_whisker_stems1)
    fig.segment(bin_centers, counts, bin_centers, counts+deltas2, line_width=vline_width, line_color=whisker_color,name=name_whisker_stems2)
    #horizontal
    fig.rect(bin_centers, counts+deltas1, whisker_breadth, hline_width, line_color=whisker_color,color="white",name=name_whisker_caps1)
    fig.rect(bin_centers, counts+deltas2, whisker_breadth, hline_width, line_color=whisker_color,color="white",name=name_whisker_caps2)
    #draw centers last above everything else
    fig.scatter(bin_centers,counts,size=point_size,color=center_color,name=name_centers) 
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
     
import matplotlib as mpl
import matplotlib.cm as cm
def classic_heatmap(x,y,c,xmin,xmax,xbins,ymin,ymax,ybins,fig=None,quad_name="quads",cmap = cm.gist_earth):
    """i plot the 2d histogram using bokeh.quad;
    over x axis i plot histogram with xbins of the xname variable between xmin and xmax
    over y axis i plot histogram with ybins of the yname variable between ymin and ymax
    the cmap argument has to be a matplotlib.cm colormap"""

    if fig is None:
        fig = figure()

    #compute color codes using the given cmap
    norm = mpl.colors.Normalize(vmin=np.min(c), vmax=np.max(c))
    mapper = cm.ScalarMappable(norm,cmap)
    colors_int = (mapper.to_rgba(c)*256).astype(int)

    ascode = lambda (r,g,b,a):"#{:02x}{:02x}{:02x}".format(r,g,b)
    color_codes = np.apply_along_axis(ascode,-1,colors_int)

    #compute size of bins
    bin_halfwidth = 0.5*(xmax-xmin)/float(xbins)
    bin_halfheight = 0.5*(ymax-ymin)/float(ybins)

    fig.quad(left = x - bin_halfwidth,right = x + bin_halfwidth,
             top = y +bin_halfheight,bottom = y - bin_halfheight,
             color=color_codes,name=quad_name)

    return fig


def draw_2d_hist_from_es(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index="*",ax = None,
                 cmap = cm.gist_earth,quad_name="quads"):
    """i plot the 2d histogram (heatmap) of a variables xname and yname 
    between [xmin,xmax],[ymin,ymax] with [xbins,ybins] uniform bins respectively.
    i require es to be an elasticsearch.Elasticsearch client"""
    
    x,y,c = get_2d_hist(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index=index)
    x,y,c = map(np.array,[x,y,c])
    ax = classic_heatmap(x,y,c,xmin,xmax,xbins,ymin,ymax,ybins,
                       fig=ax,cmap=cmap,quad_name=quad_name)

    return ax


from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.plotting import figure
from bokeh.resources import INLINE

def fig_to_html(fig,title="figure"):
    """convert bokeh figure into html string the easy way"""
    doc = Document()
    doc.add(fig)
    return file_html(doc,INLINE,title)

