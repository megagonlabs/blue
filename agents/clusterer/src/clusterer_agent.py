###### OS / Systems
from ctypes import util
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append("./lib/platform/")
sys.path.append("./lib/utils/")

######
import time
import argparse
import logging
import time

import random

###### Parsers, Formats, Utils
import csv
import json
from utils import json_utils
from string import Template
import copy
import re
import itertools
from tqdm import tqdm

##### Clustering
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent, AgentFactory
from session import Session
from producer import Producer
from consumer import Consumer

from message import Message, MessageType, ContentType, ControlCode
import util_functions
import ui_builders

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class ClustererAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "CLUSTERER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()
    
    def build_plan(self, plan_dag, stream, id=None):
        
        # create a plan id
        if id is None:
            id = util_functions.create_uuid()
        
        # plan context, initial streams, scope
        plan_context = {"scope": stream[:-7], "streams": {plan_dag[0][0]: stream}}
        
        # construct plan
        plan = {"id": id, "steps": plan_dag, "context": plan_context}

        return plan

    def write_to_new_stream(self, worker, content, output, id=None, tags=None, scope="worker"):
        # create a unique id
        if id is None:
            id = util_functions.create_uuid()

        if worker:
            output_stream = worker.write_data(
                content, output=output, id=id, tags=tags, scope=scope
            )
            worker.write_eos(output=output, id=id, scope=scope)

        return output_stream

    def issue_sql_query(self, query, worker, id=None):
        # query plan
        
        query_plan = [
            [self.name + ".Q", "QUERYEXECUTOR.DEFAULT"],
            ["QUERYEXECUTOR.DEFAULT", self.name+".QUERY_RESULTS"],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return
    
    def issue_openai_call(self, query, worker, id=None):
        # query plan
        logging.info(query)
        query_plan = [
            [self.name + ".Q", "OPENAI_LABELER.DEFAULT"],
            ["OPENAI_LABELER.DEFAULT", self.name+".OPENAI_RESULTS"],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return
    
    # TODO
    def create_visualization(self, df):
        return #Put things in vega lite template to renderm, don't do it through matplotlib 
    
        # embedded_data = TSNE(n_components=2, random_state=42).fit_transform(df.drop([self.properties'exclude_columns'], axis=1))
        # labels = df['cluster_labels_names'].values
        # unique_labels = np.unique(labels)

        # # Create scatter plot for each unique label
        # for label in unique_labels:
        #     mask = labels == label
        #     plt.scatter(x=embedded_data[mask, 0], 
        #                 y=embedded_data[mask, 1], 
        #                 cmap='viridis',
        #                 label=f'Cluster {label}',
        #                 alpha=0.25,
        #                 s=20)
        # plt.legend()

        #TODO Display visualization to user

    # Create dict {cluster_label: {cluster_size, distinctive_features}}
    def cluster_analysis(self, df, label_column, exclude_cols=[]):
        feature_cols = [col for col in df.columns 
                   if col not in [label_column] + exclude_cols]
        clusters = sorted(df[label_column].unique())
        results = {}

        # Calculate per-cluster normalized diffs all at once
        cluster_means = df.groupby(label_column)[feature_cols].mean()
        overall_means = df[feature_cols].mean()
        normalized_diff = (cluster_means - overall_means) / overall_means
        
        for cluster in clusters:
            cluster = int(cluster)
            results[cluster] = {}

            cluster_indicator = (df[label_column] == cluster)
            results[cluster]['cluster_size'] = int(cluster_indicator.sum())

            cluster_data = normalized_diff.loc[cluster].sort_values(ascending=False)
            top_features = {str(idx): f'{val:+.2%}' for idx, val in cluster_data.head(10).items()}
            bottom_features = {str(idx): f'{val:+.2%}' for idx, val in cluster_data.tail(10).items()}
            results[cluster]['distinctive_features'] = [top_features, bottom_features]
        
        return results
  
    # Creates copy of DF with one-hot-encoded and scaled cols, omitting all categories that don't meet count cutoff
    def preprocess_for_clustering(self, df, min_category_fraction=0.001, exclude_columns=[]):
        df_processed = df.copy()
        
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        categorical_columns = [col for col in categorical_columns if col not in exclude_columns]
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        numerical_columns = [col for col in numerical_columns if col not in categorical_columns and col not in exclude_columns]
        
        # Handle null values
        # Fill numerical nulls with median
        for col in numerical_columns:
            if df_processed[col].isnull().any():
                median_val = df_processed[col].median()
                df_processed[col] = df_processed[col].fillna(median_val)
        # Fill categorical nulls with 'Missing'
        for col in categorical_columns:
            if df_processed[col].isnull().any():
                df_processed[col] = df_processed[col].fillna('Missing')
        
        # One hot encode columns
        encoded_columns = []
        for col in categorical_columns:        
            encoded = pd.get_dummies(
                df_processed[col],
                prefix=col,
                drop_first=False
            )
            encoded_columns += list(encoded.columns)
            df_processed = pd.concat([df_processed, encoded], axis=1)
        # Remove original categorical columns
        df_processed.drop(categorical_columns, axis=1, inplace=True)

        # Remove categories that don't meet cutoff
        too_small_categories = []
        for col in encoded_columns:
            if df_processed[col].sum()/len(df_processed) <= min_category_fraction:
                too_small_categories.append(col)
        df_processed.drop(too_small_categories, axis=1, inplace=True)
        
        # Scale numerical columns
        if numerical_columns:
            for col in numerical_columns:
                df_processed[col] = (df_processed[col] - df_processed[col].min()) / (df_processed[col].max() - df_processed[col].min())
        
        return df_processed.groupby(self.properties['id_column']).max()

    def run_clustering(self, worker, results):
        # TODO Create option to use resume embeddings
        # if self.properties['use_resumes']:
        #     df = None
        #     pass
        # else:

        df = pd.DataFrame(results)
        exclude_columns = self.properties['exclude_columns'] + [self.properties['id_column']]
        df = self.preprocess_for_clustering(df, exclude_columns=exclude_columns)

        # TODO Option to self-determine best number of clusters
        if len(self.properties['exclude_columns']) > 0:
            cluster_df = df.drop(self.properties['exclude_columns'], axis=1)
        else:
            cluster_df = df
        model = KMeans(n_clusters = self.properties['num_clusters'], random_state=1).fit(cluster_df)
        df['cluster_labels'] = model.labels_

        analysis = self.cluster_analysis(df, 'cluster_labels', exclude_cols=exclude_columns)
        logging.info(analysis)
        self.issue_openai_call(analysis, worker)

        # Save data
        self.df = df


    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        logging.info('Entering processor')
        ##### Upon USER input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()
                logging.info(message.getData())
                stream_data = ""
                if worker:
                    session_data = worker.get_all_session_data()
                    logging.info(worker.session.cid)
                    logging.info(json.dumps(session_data, indent=3)) 

                    if session_data is None:
                        session_data = {}

                    # user initiated summarizer, kick off queries from template
                    self.results = {}

                    # db queries
                    if 'queries' in self.properties:
                        queries = self.properties['queries']
                        for query_id in queries:
                            q = queries[query_id]
                            if type(q) == dict:
                                q = json.dumps(q)
                            else:
                                q = str(q)
                            query_template = Template(q)
                            query = query_template.safe_substitute(**self.properties, **session_data)
                            self.issue_sql_query(query, worker, id=query_id)

                    return

            elif message.isBOS():
                stream = message.getStream()

                # init private stream data to empty array
                if worker:
                    worker.set_data(stream, [])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                stream = message.getStream()

                # append to private stream data
                if worker:
                    worker.append_data(stream, data)

        elif input == "QUERY_RESULTS":
            if message.isData():
                stream = message.getStream()

                # get query from incoming stream
                query = stream[stream.find("Q"):].split(":")[1]

                data = message.getData()

                # logging.info(data)
            
                if 'result' in data:
                    self.results = data['result']
                    # Perform clustering on query results
                    self.run_clustering(worker, self.results)

                else:
                    logging.info("nothing found")

        elif input == "OPENAI_RESULTS":
            if message.isData():
                stream = message.getStream()
                data = message.getData()
                logging.info(data)

                if 'result' in data:
                    cluster_label_mapping = json.dumps(data['result'])
                    logging.info(cluster_label_mapping)
                    self.df['cluster_labels_names'] = list(map(cluster_label_mapping.get, self.df['cluster_labels']))

                    if self.properties['create_visualization']:
                        self.create_visualization(self.df)

                    # TODO construct table from analysis and give to user
                    analysis = self.cluster_analysis(self.df, 'cluster_labels_names', ['cluster_labels'])
                    self.write_to_new_stream(worker, analysis, "R") 
                else:
                    logging.info('Nothing found')



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="CLUSTERER", type=str)
    parser.add_argument("--session", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str)
    parser.add_argument("--platform", type=str, default="default")
    parser.add_argument("--registry", type=str, default="default")

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    if args.serve:
        platform = args.platform

        af = AgentFactory(
            _class=ClustererAgent,
            _name=args.serve,
            _registry=args.registry,
            platform=platform,
            properties=properties,
        )
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = ClustererAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = ClustererAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:

            session.wait()
