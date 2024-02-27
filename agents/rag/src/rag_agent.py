###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/utils/')

###### 
import time
import argparse
import logging
import time
import uuid
import random
import pandas as pd

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent
from session import Session

# set log level
logging.getLogger().setLevel(logging.INFO)

###### Agent-specific
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.faiss import FaissVectorStore


#######################


class RAGAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("RAG", session=session, input_stream=input_stream, processor=processor, properties=properties)        
        # initialize rag pipeline
        #self._initialize_rag(properties)
        self._initialize(properties)
        
    
    def _initialize(self, properties):
        super()._initialize_properties()
        super()._update_properties(properties)  
        properties['query_engine'] = self._load_index(properties).as_query_engine(similarity_top_k=properties['top_k'], 
                                                                            streaming=True)
        super()._update_properties(properties)
    
    def _resolve_llm(self, properties):
        if 'gpt-' in self.properties['llm_model_str']: # open-ai models start with gpt-
            return OpenAI(model=properties['llm_model_str'], 
                          api_key=properties['openai_api_key'], 
                          temperature=properties['llm_temperature'])
        else:
            return HuggingFaceLLM(model_name=properties['llm_model_str'],
                                  generate_kwargs={
                                      "temperature": properties['temperature']
                                  })
    def _resolve_embed_model(self, properties):
        return HuggingFaceEmbedding(model_name=properties['embed_model_str'],
                                    pooling=properties['embed_model_pool'])


    def _load_index(self, properties):
        Settings.llm = self._resolve_llm(properties)
        Settings.embed_model = self._resolve_embed_model(properties)  
        vector_store = FaissVectorStore.from_persist_dir(properties['persist_dir'])
        storage_context = StorageContext.from_defaults(vector_store=vector_store,
                                                            persist_dir=properties['persist_dir'])
        return load_index_from_storage(storage_context=storage_context)

    def _execute_query(self, query):
        return self.query_engine.query(' '.join(query))
    

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        if label == 'EOS':
            # compute stream data
            if worker:
                query = worker.get_data('stream')
                if len(query):
                    response = properties['query_engine'].query(' '.join(query))
                    logging.info(response)
                    # output to stream
                    return response
            return None
        elif label == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif label == 'DATA':
            # store data value
            logging.info(data)
            
            if worker:
                worker.append_data('stream', data)
    
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())


    session = None
    a = None

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)
    
    if args.session:
        # join an existing session
        session = Session(args.session)
        a = RAGAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = RAGAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = RAGAgent(properties=properties)
        session = a.start_session()


    # wait for session
    session.wait()


