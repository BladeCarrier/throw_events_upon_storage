__doc__="""Library with everything about events representation"""

import ROOT
from root_numpy import random_sample

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
# name: TFile
histFiles = { feature: ROOT.TFile(hist_paths[feature]) for feature in hist_paths}
# name: root histogram (TH*)
hists = { feature: histFiles[feature].Get(hist_branches[feature]) for feature in hist_paths}
    
    
    



es_event_mapping = {
    "_source" : { "enabled" : False },
    "properties" : {
        "muonHits" : { "type" : "float","index" : "not_analyzed" },
        "hcalEnergy" : { "type" : "float","index" : "not_analyzed" },
        "avgMass"  : { "type" : "float","index" : "not_analyzed" },

    }
}

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
    
