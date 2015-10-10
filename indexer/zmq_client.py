__doc__="""zmq package identification functions and a client interface to interact with zmq_event_bus.Bus server on the same port"""
import zmq
import pickle

class Client:
    """i am a client interface to interact with zmq_event_bus.Bus server on the same port"""
    def __init__(self,port='tcp://127.0.0.1:43000'):
        """i am a client interface to interact with zmq_event_bus.Bus server on the same port"""
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(port)

    def get(self):
        """get the next server package (event package or run_id update)"""
        self.socket.send(pickle.dumps('get'))
        return pickle.loads(self.socket.recv()) #event structure OR new run_id
    
    def send(self, data):
        """sent events to the bus for them to be accessible via Client.get"""
        self.socket.send(pickle.dumps(data))
        return self.socket.recv() == b'ok'
    
    def ask_runid(self):
        """request the server to send run_id"""
        self.socket.send(pickle.dumps('gimme_runid'))
        return self.socket.recv() == b'ok'
    
def is_runid(package):
    return (type(package) is int)
def is_request(package):
    return (type(package) is str)
def is_empty(package):
    return (package is None)

def is_events(package):
    return not(is_runid(package) or is_request(package) or is_empty(package))


