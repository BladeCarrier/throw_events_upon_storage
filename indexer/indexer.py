__doc__='''a class that takes packages from the server and sends it to the ES '''
import elasticsearch
import time
import json
import zmq_client
import event


class Indexer:
    '''a class that takes packages from the server and sends it to the ES '''
    def __init__(self,es_port="http://localhost:9200/",zmq_port='tcp://127.0.0.1:43000',verbose=False):
        
        self.es = elasticsearch.Elasticsearch([es_port])
        self.client = zmq_client.Client(zmq_port)
        self.verbose = verbose
        self.current_run_id = None

    def create_index(self,index_name):
        """create new index to store events in"""
        answer = self.es.indices.create(index_name,body={"mappings":{"event":event.es_event_mapping}})
        return answer[u'acknowledged']

    def start_indexing(self):
        """main loop that takes events from the bus and saves them into the indices corresponding to their run_id"""
        client = self.client
        verbose = self.verbose
        es = self.es
        while(True):
            package = client.get()
            
            #if got run_id, save it
            if zmq_client.is_runid(package):
                if verbose:
                    print "run id recieved:",package
                    n_events_in_run = 0
                    
                self.current_run_id = "run"+str(package)
                es.indices.flush()
                if not es.indices.exists(self.current_run_id):
                    self.create_index(self.current_run_id)
                    if verbose:
                        print "new index created:",self.current_run_id 

                continue
            
            #if run_id is not known, request it and skip until got it
            if self.current_run_id is None:
                client.ask_runid()
                if verbose:
                    print "requesting run id..."
                continue

            #empty queue
            if zmq_client.is_empty(package):
                if verbose:
                    print "queue empty"
                continue
            #package is a bunch of events
            #handle events:
            if verbose:
                print "processing events..."
            events= event.from_zmq_package(package)
            
            for evt in events:
                es.index(index=self.current_run_id,
                         doc_type="event",
                         id=n_events_in_run,
                         body=evt)
                n_events_in_run+=1

                
            if verbose:
                print n_events_in_run,"events indexed in current run_id"

            
                
               
            
        

if __name__ == "__main__":
    print "TODO!!!"
