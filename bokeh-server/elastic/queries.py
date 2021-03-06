__doc__ = """this module knows how to transform ElasticSearch aggregation output into histogram-ready data"""
from scripts import realValueHistogram, heatmap

def parse_terms_1d(data,xmin,xmax,n_bins,starting_id=0):
    """takes ElasticSearch.search aggregaton buckets as an input and 
    returns a list of tuples[(bucket_center,count)].
    !!!WARNING!!! the elastic_scripts.conventionalRealValueHistogram does not require
    this function as it already returns bucket centers instead of bucket ids"""
    data_dict= { int(float(d[u"key"]))-starting_id:d[u"doc_count"] for d in data}
    
    bin_width = (xmax-xmin)/float(n_bins)
    bin_bounds = [xmin + bin_width*i for i in xrange(n_bins)]+[xmax]
    hist_bins =  [ (0.5*(bin_bounds[i]+bin_bounds[i+1]),data_dict.get(i,0)) for i in xrange(n_bins)]
    return hist_bins

def get_1d_hist(xname,xmin,xmax,xbins,es,index="*"):
    """i assemble the histogram of a variable xname between xmin,xmax with xbins uniform bins.
    i require es to be an elasticsearch.Elasticsearch client.
    Output: [X_bin_centers],[bin_counts"""
    query_dsl = {
        "aggs" : {
            "1d_hist" : realValueHistogram(xname,xmin,xmax,xbins)

        }
    }
    data = es.search(index=index,body=query_dsl)["aggregations"]["1d_hist"]["buckets"]

    bins_list = parse_terms_1d(data,xmin,xmax,xbins)
    return zip(*bins_list)





from itertools import groupby
def parse_terms_2d(data,xmin,xmax,xbins,ymin,ymax,ybins):
    """takes ElasticSearch.search aggregaton buckets as an input and
    returns a list of tuples[(bucket_center_x,bucket_center_y,count)].
    """
    hist_bins = [] # [ (xcenter,ycenter, count) for all bins ]
    
    #group all keys by rows (constant Y)
    xgroups = groupby(sorted(data,key=lambda d: float(d[u"key"])),lambda d: int(float(d[u"key"]))/xbins)
    
        
    ybin_width = (ymax-ymin)/float(ybins)
    ybin_bounds = [ymin + ybin_width*i for i in xrange(ybins)]+[ymax]

    
    for ybin_id,xgroup in xgroups:
        y = 0.5*(ybin_bounds[ybin_id]+ybin_bounds[ybin_id+1])

        bins_list = parse_terms_1d(list(xgroup),xmin,xmax,xbins,
                                   starting_id = ybin_id*xbins)
        hist_bins += [ (x,y,count) for (x,count) in bins_list]
    return hist_bins


def get_2d_hist(xname,xmin,xmax,xbins,
                 yname,ymin,ymax,ybins,
                 es,index="*",generator='default'):
    """i plot the 2d histogram (heatmap) of a variables xname and yname 
    between [xmin,xmax],[ymin,ymax] with [xbins,ybins] uniform bins respectively.
    i require es to be an elasticsearch.Elasticsearch client
    "generator" arg determines the way Lucene Expression scripts are generated,
        generator = "default" or "two-trees" generates 2 separate trees for X and Y and returns x_tree + x_bins*y_tree
        generator = "single-tree" generates one tree that returns both X and Y 
    Output: [x_bin_center],[y_bin_center],[bin_count]"""
    
    query_dsl = {
        "aggs" : {
            "2d_hist" : heatmap(xmin,xmax,xbins,xname,ymin,ymax,ybins,yname,generator)

        }
    }
    data = es.search(index=index,body=query_dsl)["aggregations"]["2d_hist"]["buckets"]

    bins_list = parse_terms_2d(data,xmin,xmax,xbins,ymin,ymax,ybins)

    return zip(*bins_list)
    

