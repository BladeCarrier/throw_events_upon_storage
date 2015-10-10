__doc__="""DIM/ZMQ bus emulator that interacts with zmq_client.Client on the same port"""
import pickle
import zmq
import zmq_client
import Queue
import event
import time
import numpy as np

class Bus:
    '''DIM/ZMQ bus emulator that interacts with zmq_client.Client on the same port'''
    
    def __init__(self,
                 port = 'tcp://127.0.0.1:43000',
                 verbose = True,
                 dtime = 0,#time between main loop iterations
                 n_events_per_run_id = 3e4,
                 n_events_variance_per_run_id = 2e4,                 
                 generate_events = True, #generate fake events via event.generate_package if queue is empty
                 n_events_per_package=5e2, #only concerns generated events
                 n_events_variance_per_package=2e2, #only converns generated events
                 ):
        '''DIM/ZMQ bus emulator that generates events'''
        
        self.port=port
        self.verbose=verbose
        self.dtime = dtime
        self.eventQueue = Queue.Queue();
        
        #event generation
        self.generate_events = generate_events
        self.n_events_per_package = n_events_per_package
        self.n_events_variance_per_package = n_events_variance_per_package

        #run id switch
        self.current_run_id = 15000
        self.client_run_id_obsolete = True
        self.n_events_per_run_id = n_events_per_run_id
        self.n_events_variance_per_run_id = n_events_variance_per_run_id
        self.events_until_next_run = max(1,int(np.random.normal(self.n_events_per_run_id,
                                                        self.n_events_variance_per_run_id))) 
    def run_server(self):
        """launch it..."""
        
        dtime = self.dtime
        port = self.port
        qq = self.eventQueue
        verbose = self.verbose
        
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(port)
        
        if verbose:
            print "server online..."

        while True:
            package = pickle.loads(socket.recv())
            if zmq_client.is_request(package):
                #package is 'get' or 'gimme_runid'
                
                if package == "get":
                    #client requests feed
                    
                    if self.client_run_id_obsolete:
                        #update client run_id information (on request or when switching run_ids)
                        socket.send(pickle.dumps(self.current_run_id))
                        self.client_run_id_obsolete = False
                    
                    elif not qq.empty():
                        #give out queued package
                        socket.send(pickle.dumps(qq.get()))
                        
                    elif self.generate_events:#also qq.empty() is True
                        #generate events package
                        n_events = int(np.random.normal(self.n_events_per_package,
                                                        self.n_events_variance_per_package))
                        n_events = max(1,n_events) #in case of a negative number
                        n_events = min(n_events,self.events_until_next_run) #cut at the end of run_id
                        
                        package = event.generate_zmq_package(n_events)
                        socket.send(pickle.dumps(package))
                        
                        self.events_until_next_run -= n_events
                        
                        if self.events_until_next_run <=0:
                            #going to the next run
                            self.current_run_id +=1
                            self.events_until_next_run = max(1,int(np.random.normal(self.n_events_per_run_id,
                                                        self.n_events_variance_per_run_id)))  
                            self.client_run_id_obsolete = True
                            if verbose:
                                print "announcing run_id",self.current_run_id
                        
                    else: #qq.empty is True, self.generate_events is False
                        #signalize that queue is empty
                        socket.send(pickle.dumps(None))
                        
                        
                else: # package == "gimme_runid"
                    #client requests run_id
                    #queue giving out the current run_id
                    self.client_run_id_obsolete = True
                    socket.send("ok")
                    if verbose:
                        print "client requested run_id"
                    
            else:#not zmq_client.is_request(package)
                #someone asks us to queue up the pacakge for the indexer
                qq.put(package)
                socket.send("ok")
                    
                
            time.sleep(dtime)


        
if __name__ == "__main__":
    import sys
    
    try:
        bus = Bus(*sys.argv[1:])
        bus.run_server()

    except e:
        print "Error happened:",e
        print "args list with defaults:"
        print """
                 port = 'tcp://127.0.0.1:43000',
                 verbose = False,
                 dtime = 0,#time between main loop iterations
                 n_events_per_run_id = 5e3,
                 n_events_variance_per_run_id = 1e3,                 
                 generate_events = True, #generate fake events via event.generate_package if queue is empty
                 n_events_per_package=1e3, #only concerns generated events
                 n_events_variance_per_package=5e2, #only converns generated events
                 """
        
         
