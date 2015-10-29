# -*- coding: utf-8 -*-
__doc__="i am a script to start indexing data to the ES"

import os
os.system('python indexer/zmq_event_bus.py &')


import indexer.indexer as indexer
import time
while True:
    try:
        inder = indexer.Indexer(verbose=True)
        #начинаем складывать ивенты в индексы. 
        inder.start_indexing()
    except:
        time.sleep(15);
        pass
