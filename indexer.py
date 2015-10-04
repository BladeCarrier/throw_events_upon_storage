import elasticsearch
import time
import json
from zmq_client import Client

es_port="http://localhost:9200/"
zmq_port='tcp://127.0.0.1:43000'
index_name="stored-events"

def start_indexing(create_index=True,verbose=False):
    #initialize
    es = elasticsearch.Elasticsearch([es_port]) #in current project configuration

    #create
    if create_index:
        es.indices.create(index=index_name, ignore=400)
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
            es.index(index=index_name,
                     doc_type="events-bunch",
                     id=i,
                     body={
                        "events":json.dumps(list(ans)),
                        "timestamp":json.dumps(list(gmtime))
                        })
            i+=1
            if verbose:
                print gmtime, "events indexed"

if __name__ == "__main__":
    start_indexing()