import pickle
import json
import zmq
import Queue

port = 'tcp://127.0.0.1:43000'

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(port)

qq = Queue.Queue()

print "server online"
while True:
    
    stuff = pickle.loads(socket.recv())
    if type(stuff) is str:
        #'get'
        if qq.empty():
            socket.send(pickle.dumps(None))
        else:
            socket.send(pickle.dumps(qq.get()))
    else:
        qq.put(stuff)
        socket.send("ok")
