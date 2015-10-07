import pickle
import json
import zmq
import Queue
import ROOT



##generate arrays: init
from root_numpy import random_sample
import time
addr= "hists/Moore1HistAdder-154831-20150614T045352-EOR.root"
hist_branch="Hlt1RoutingBitsWriter/RoutingBit33"
rfile = ROOT.TFile(addr)
hist = rfile.Get(hist_branch)
#/


##server init

qq = Queue.Queue()
#/

##main loop
def run_server(port = 'tcp://127.0.0.1:43000',
                n_events_per_bunch=1e3,
                dtime = 0.1
                ):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(port)
    print "server online"

    while True:

        stuff = pickle.loads(socket.recv())
        if type(stuff) is str:
            #'get'
            if qq.empty():
                arr = random_sample(hist, n_events_per_bunch)
                if len(arr)==1:arr = arr[0]
                socket.send(pickle.dumps(arr))
            else:
                socket.send(pickle.dumps(qq.get()))
        else:
            qq.put(stuff)
            socket.send("ok")
#/
if __name__ == "__main__":
    import sys
    run_server(*sys.argv[1:])