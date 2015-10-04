import zmq
import pickle

class Client:
    def __init__(self,addr='tcp://127.0.0.1:43000'):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(addr)

    def get(self):
        self.socket.send(pickle.dumps('get'))
        return pickle.loads(self.socket.recv())

    def send(self, data):
        self.socket.send(pickle.dumps(data))
        return self.socket.recv() == b'ok'