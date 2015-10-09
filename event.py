__doc__="""Library with everything about events representation"""

import ROOT
from root_numpy import random_sample

es_type_float= { "type" : "float","index" : "not_analyzed" }
es_type_int = { "type" : "int","index" : "not_analyzed" }
es_event_mapping = {
    "_source" : { "enabled" : False },
    "properties" : {
        "muonHits" : es_type_float,
        "hcalEnergy" : es_type_float,
        "avgMass"  : es_type_float,

    }
}

# name: file_path
hist_paths = { 
    "muonHits": "hists/Moore1HistAdder-154803-20150614T005209-EOR.root",
    "hcalEnergy": "hists/Moore1HistAdder-154807-20150614T015931-EOR.root",
    "avgMass": "hists/Moore1HistAdder-154825-20150614T042801-EOR.root",
    }
# name: branch
hist_branches = { 
    "muonHits": "Hlt1RoutingBitsWriter/RoutingBit33",
    "hcalEnergy": "Hlt1RoutingBitsWriter/RoutingBit33",
    "avgMass": "Hlt1RoutingBitsWriter/RoutingBit33",
    }

#dummies
def _add_dummies(n_dummies):
    """add some dummy variables to make event look like a real one"""
    import os
    import random
    all_hists =filter( lambda tfile_name: tfile_name.endswith(".root"), os.listdir("hists"))

    for i in xrange(n_dummies):
        hist_name = random.choice(all_hists)
        hist_path =  os.path.join("hists",hist_name)
        var_name = "dummy"+str(i)
        hist_branches[var_name] = hist_path
        hist_branches[var_name] = "Hlt1RoutingBitsWriter/RoutingBit33"
        es_event_mapping["properties"][var_name] = es_type_float
_add_dummies(int(1e4))
#/dummies

# name: TFile
histFiles = { feature: ROOT.TFile(hist_paths[feature]) for feature in hist_paths}
# name: root histogram (TH*)
hists = { feature: histFiles[feature].Get(hist_branches[feature]) for feature in hist_paths}
    
    
    




def generate_zmq_package(n_events=1):
    #n_events -> package with that many events
    package = {}
    for feature in hists.keys():
        hist = hists[feature]
        arr = random_sample(hist, n_events)
        package[feature] = arr
    return package
    
def from_zmq_package(package):
    #package -> iterator(events)
    n_events = len(package.values()[0])
    features = package.keys()               
    return ( {feature:package[feature][i] for feature in features}
            for i in xrange(n_events)) 
    
