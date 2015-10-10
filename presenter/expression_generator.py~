__doc__ = """ here lies bunch of auxilary scripts that generate Lucene Expression code. 
Surprisingly, such code chunks, being optimized and compiled to native code on the shards,
demonstrate amazing performance at what kibana simply cannot do yet"""
__author__ = """a pride hedgehog after spending night locked in YSDA"""


def binsearch_expression(xmin,xmax,n_bins,starting_id=0,
                         variable_name = "_value",
                         bin_format = lambda bin_id: str(bin_id),
                        ):
    """generates an expression script that returns bin id in a histogram via binsearch.
    Bin id starts from 0 and increases in positive X direction.
    The script itself is O(n_bins*log(2,n_bins)) code length and O(log(n_bins)) execution time.
    The script is meant to be used inside terms aggreagation for elasticsearch to return (bin_id, count) pairs.
    Expression script than gets heavily optimized by Lucene on the server side.
    """
    if n_bins == 1:
        return str(bin_format(starting_id))
    
    diff = xmax-xmin
    lower_bins = int(n_bins/2)
    pivot = xmin + diff*lower_bins/float(n_bins)
    
    lower_subtree = binsearch_expression(xmin,pivot,lower_bins,
                                         starting_id=starting_id,
                                         bin_format=bin_format,
                                         variable_name = variable_name)
    upper_subtree = binsearch_expression(pivot,xmax,n_bins-lower_bins,
                                         starting_id=starting_id+lower_bins,
                                         bin_format=bin_format,
                                         variable_name = variable_name)
    return "({}>{}?{}:{})".format(variable_name,pivot,upper_subtree,lower_subtree)

def heatmap_expression(xmin,xmax,xbins,ymin,ymax,ybins,xname="doc['var1'].value",yname="doc['var2'].value"):
    """like the binsearch_expression (and based on it), generates an expression script that
    maps data into bin_id on a 2D histogram (a.k.a. heatmap) over x and y.
    Bin ids are defined as x_bin_id + y_bin_id*xbins, both bin_ids starting from 0 and increasing over the corresponding axes (x or y)
    The expression itself is O(n_bins*log(2,n_bins)) code length and O(log(n_bins)) execution time, where n_bins = xbins*ybins.
    The script is meant to be used inside terms aggreagation for elasticsearch to return (bin_id, count) pairs.
    Expression script than gets heavily optimized by Lucene on the server side.
    """

    
    def _outerbinformat(y_id):
        return binsearch_expression(xmin,xmax,xbins,
                                    variable_name = xname,
                                    bin_format=lambda x_id:y_id*xbins+x_id,
                                    )
        
    return binsearch_expression(ymin,ymax,ybins,
                                      variable_name= yname,
                                      bin_format= _outerbinformat
                                     )

