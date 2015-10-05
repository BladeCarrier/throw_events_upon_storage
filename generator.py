import ROOT
from root_numpy import random_sample
from zmq_client import Client
import time

addr= "hists/Moore1HistAdder-154831-20150614T045352-EOR.root"
hist_branch="Hlt1RoutingBitsWriter/RoutingBit33"
zmq_port='tcp://127.0.0.1:43000'
n_events_per_bunch=1e6
dtime = 0.1

def start_sending(verbose=False):
    rfile = ROOT.TFile(addr)
    hist = rfile.Get(hist_branch)
    client = Client(zmq_port)
    
    while True:
        arr = random_sample(hist, n_events_per_bunch)
        client.send(arr)
        if dtime>0:
            time.sleep(dtime)
        if verbose:
            print n_events_per_bunch,"sent"

if __name__ == "__main__":
    start_sending()