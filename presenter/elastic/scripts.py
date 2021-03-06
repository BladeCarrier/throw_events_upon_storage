__doc__= """
Here you may find scripts that modify aggregations elasticSearch aggregation
to allow for various stuff yet unimplemented in ES itself.
The functions withis this module return DICTIONARIES that may be embedded into
the "aggs" part of the es.search body as named aggregations
Example usage:

import elasticsearch
es = elasticsearch.Elasticsearch(["localhost:9200"]) #Or wherewer you have it

from elastic_scripts import realValueHistogram

query_dsl = {
    "aggs" : {
        "epyk_name" : realValueHistogram("muonHits",0,20,7)
    }
}

es.search(index="run*",body=query_dsl)["aggregations"]["epyk_name"]["buckets"]
Out[3]:
[{u'doc_count': 192541, u'key': 6.0},
 {u'doc_count': 12469, u'key': 3.0},
 {u'doc_count': 12418, u'key': 4.0},
 {u'doc_count': 12415, u'key': 5.0},
 {u'doc_count': 12306, u'key': 2.0},
 {u'doc_count': 12258, u'key': 1.0},
 {u'doc_count': 5271, u'key': 0.0}]
 """
__author__ = """a pride hedgehog after spending night locked in YSDA"""


def conventionalRealValueHistogram(field_name, interval, max_bins =0):
    """A histogram with arbitrary interval [ES only supports integer so far],
    that is achieved by mapping field to its closest interval without code generation.
    This might (or might not) be more efficient, than the code generation approach 
    (realValueHistogram), but they both are probably slower than the conventional 
    ElasticSearch histogram aggragation, provided interval is an integer.
    !!!WARNING!!! the keys definition here differs from the realValueHistogram output (bin centers vs bin ids)
    Search output: "Terms" aggregation bins (key:bin_center, doc_count:count), e.g. 
    {u'buckets': [
    {u'doc_count': 614, u'key': 3.2},
    {u'doc_count': 569, u'key': 1.7000000000000002},
    {u'doc_count': 558, u'key': 3.4000000000000004},
    {u'doc_count': 557, u'key': 2.7}
    ],
    u'doc_count_error_upper_bound': 0,
    u'sum_other_doc_count': 100500}},
    }
    """
                       
    agg={
        "terms": {
                "field": field_name,
                "script" : "_value % interval < 0 ? _value -((_value % interval) + interval) : (_value - (_value % interval))",
                "lang" : "expression" ,
                'size' : max_bins,
                "params": {
                    "interval" : interval
                          }
                }#/terms
    }#/agg
    return agg

from expression_generator import binsearch_expression, heatmap_expression,heatmap_expression_one_tree

def realValueHistogram(field_name, xmin,xmax, n_bins):
    """
    A histogram of the field_name values with arbitrary n_bins, at uniform intervals between xmin and xmax.
    
    !!!WARNING!!! the keys definition here differs from the realValueHistogram output (bin centers vs bin ids)

    Search output: "Terms" aggregation bins (key:bin_number, doc_count:count), e.g. 
    Bin id starts from 0 and increases in positive X direction.
    
    {u'buckets': [
    {u'doc_count': 614, u'key': 0.0},
    {u'doc_count': 569, u'key': 1.0},
    {u'doc_count': 558, u'key': 2.0},
    {u'doc_count': 557, u'key': 3.0}
    ],
    u'doc_count_error_upper_bound': 0,
    u'sum_other_doc_count': 100500}},
    }
    """
    agg={
    "terms": {
                "field": field_name,
                "script" : binsearch_expression(xmin,xmax,n_bins),
                "lang" : "expression" ,
                'size' : "0",
                }#/terms
    }#/agg
    return agg

    

def heatmap(xmin,xmax,xbins,xname,ymin,ymax,ybins,yname,generator = 'default'):
    """
    A 2D histogram of the (xname,yname values with arbitrary amount bins over x and y (xbins and ybins),
    bins corresponding to uniform intervals between xmin and xmax.
    
    xname and yname must be string names of variables as specified in index (p.e. "muonHits", but NOT "doc['muonHits']")
    
    "generator" arg determines the way Lucene Expression scripts are generated,
        generator = "default" or "two-trees" generates 2 separate trees for X and Y and returns x_tree + x_bins*y_tree
        generator = "single-tree" generates one tree that returns both X and Y 

    !!!WARNING!!! the keys definition here differs from the realValueHistogram output (bin centers vs bin ids)

    Search output: "Terms" aggregation bins (key:bin_number, doc_count:count), e.g. 
    Bin id starts from 0 and increases in positive X direction.
    
    {u'buckets': [
    {u'doc_count': 614, u'key': 0.0},
    {u'doc_count': 569, u'key': 1.0},
    {u'doc_count': 558, u'key': 2.0},
    {u'doc_count': 557, u'key': 3.0}
    ],
    u'doc_count_error_upper_bound': 0,
    u'sum_other_doc_count': 100500}},
    }
    """
    vpattern = "doc['{}'].value"
    varxname = vpattern.format(xname)
    varyname = vpattern.format(yname)
    
    if generator=='default':
        heatmap_gen = heatmap_expression  
    else:
        heatmap_gen = heatmap_expression_one_tree
    agg={
        "terms": {
                "script" : heatmap_gen(xmin,xmax,xbins,ymin,ymax,ybins,varxname,varyname),
                "lang" : "expression" ,
                'size' : "0",
                }#/terms
        }#/agg
    return agg




