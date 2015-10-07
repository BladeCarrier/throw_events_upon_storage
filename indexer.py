import elasticsearch
import time
import json
from zmq_client import Client

es_port="http://localhost:9200/"
zmq_port='tcp://127.0.0.1:43000'



def create_index(index_name,es):
    event_mapping = {
            "_source" : { "enabled" : False },
            "properties" : {
                "muonHits" : { "type" : "float"}#, "index" : "not_analyzed" }
            }
        }
    answer = es.indices.create(index_name,body={"mappings":{"event":event_mapping}})
    return answer[u'acknowledged']

def start_indexing(index_name="events-stored",
                   new_index=True,
                   verbose=False):
    #initialize
    es = elasticsearch.Elasticsearch([es_port]) #in current project configuration

    #create
    if new_index:
        create_index(index_name, es)
    client = Client(zmq_port)

    i=0
    while True:
        ans = client.get()
            
        if ans is None:
            time.sleep(0.1)
            if verbose:
                print time.gmtime(),"queue empty"
        else:
            gmtime = time.gmtime()
            ans= list(ans)
            for evt in ans:
                es.index(index=index_name,
                         doc_type="event",
                         id=i,
                         body={
                            "value":evt,
                            #"timestamp":json.dumps(list(gmtime))
                            })
                i+=1
            if verbose:
                print i,"events indexed so far"

if __name__ == "__main__":
    start_indexing()