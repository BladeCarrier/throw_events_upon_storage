__doc__ = "i draw histograms from the ELasticSearch terms aggregations"

from elastic.queries import get_1d_hist, get_2d_hist
import matplotlib.pyplot as plt


def draw_1d_hist_from_es(xname,xmin,xmax,xbins,es,index="*",ax=None):
    """i plot the histogram of a variable xname between xmin,xmax with xbins uniform bins.
    i require es to be an elasticsearch.Elasticsearch client. """
    if ax is None:
        ax = plt
    x,c = get_1d_hist(xname,xmin,xmax,xbins,es,index=index)
    return ax.hist(x,
                range = [xmin,xmax],bins= xbins ,
                weights=c)
    
def draw_2d_hist_from_es(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index="*",ax = None):
    """i plot the 2d histogram (heatmap) of a variables xname and yname 
    between [xmin,xmax],[ymin,ymax] with [xbins,ybins] uniform bins respectively.
    i require es to be an elasticsearch.Elasticsearch client"""
    if ax is None:
        ax = plt
    x,y,c = get_2d_hist(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index=index)

    return ax.hist2d(x,y,bins=[xbins,ybins],
                range = [[xmin,xmax],[ymin,ymax]],
                weights=c)

