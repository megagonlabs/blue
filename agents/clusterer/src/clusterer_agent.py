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
from sentence_transformers import SentenceTransformer
from sklearn.metrics import silhouette_score
import umap

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
    
    def issue_agent_call(self, query, worker, agent_name, results_name, stream_name, id=None):
        # query plan
        query_plan = [
            [self.name + "." + stream_name, agent_name + ".DEFAULT"],
            [agent_name + ".DEFAULT", self.name+results_name],
        ]

        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, stream_name, tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)
    
    # Show table of clusters and distinctive features to user
    def display_cluster_summaries(self, worker, analysis):
        logging.info('Creating cluster summary tables')
        values = []
        for cluster_name in analysis.keys():
            cluster_size = analysis[cluster_name]['cluster_size']
            dist_feat_high = analysis[cluster_name]['distinctive_features']
            for feat, presence in dist_feat_high.items():
                values.append({'Cluster Name': cluster_name, 'Cluster Size': cluster_size, 'Distinctive Feature': feat, 'Feature Presence Relative to Mean': presence})

        template = {
            "vega-spec": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {
                    "values": values
                },
                "transform": [
                    {"window": [{"op": "row_number", "as": "row_num"}]},
                    {"fold": ["Cluster Name", "Cluster Size", "Distinctive Feature", "Feature Presence Relative to Mean"]}
                ],
                "mark": "text",
                "encoding": {
                    "y": {"field": "row_num", "type": "ordinal", "axis": None},
                    "text": {"field": "value", "type": "nominal"},
                    "x": {"field": "key", "type": "nominal", "axis": {"orient": "top", "labelAngle": 0, "title": None, "domain": False, "ticks": False}, "scale": {"padding": 15}}
                }, "config": {"view": {"stroke": None}}}
        }

        vis_form = ui_builders.build_vis_form(template)

        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, vis_form, output="VIS"
        )

    # Show visualization of clusters in 2D scatterplot
    def create_visualization(self, worker, df):   
        logging.info('Creating dimensionality reduction visualization')

        # embedded_data = TSNE(n_components=2, random_state=self.properties['random_seed']).fit_transform(self.cluster_df)
        embedded_data = umap.UMAP(random_state=self.properties['random_seed']).fit_transform(self.cluster_df)[:, :2]
        labels = df['cluster_labels_names'].values

        values = [{"x": float(x),"y": float(y),"cluster": str(label)} for (x, y), label in zip(embedded_data, labels)]
        template = {
            "vega-spec": {"$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {
                    "values": values
                },
                "mark": {"type": "point", "size": 3},
                "encoding": {
                    "x": {
                    "field": "x",
                    "type": "quantitative",
                    "scale": {"zero": False}
                    },
                    "y": {
                    "field": "y",
                    "type": "quantitative",
                    "scale": {"zero": False}
                    },
                    "color": {"field": "cluster", "type": "nominal"},
                    "shape": {"field": "cluster", "type": "nominal"}
                }}
        }
        
        vis_form = ui_builders.build_vis_form(template)

        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, vis_form, output="VIS"
        )

    # Create dict {cluster_label: {cluster_size, distinctive_features}}
    def cluster_analysis(self, df, label_column, exclude_cols=[]):
        feature_cols = [col for col in df.columns 
                   if col not in [label_column] + exclude_cols 
                   and df[col].dtype != 'object']
        clusters = sorted(df[label_column].unique())
        results = {}

        # Calculate per-cluster normalized diffs all at once
        cluster_means = df.groupby(label_column)[feature_cols].mean()
        overall_means = df[feature_cols].mean()
        normalized_diff = (cluster_means - overall_means) / overall_means
        
        for cluster in clusters:
            if type(cluster) != type(''):
                cluster = int(cluster)
            results[cluster] = {}

            cluster_indicator = (df[label_column] == cluster)
            results[cluster]['cluster_size'] = int(cluster_indicator.sum())

            cluster_data = normalized_diff.loc[cluster].sort_values(ascending=False)
            top_features = {str(idx): f'{val:+.2%}' for idx, val in cluster_data.head(10).items()}
            results[cluster]['distinctive_features'] = top_features
        
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
        
        return df_processed.groupby(self.properties['id_column']).max().reset_index()

    def get_embeddings_df(self, df):
        logging.info('Using embeddings')
        # Read embeddings from file if it exists
        if 'text_embedding_path' in self.properties and os.path.exists(self.properties['text_embedding_path']):
            logging.info('Reading embeddings from file')
            cluster_df = pd.read_csv(self.properties['text_embedding_path'])
        else: #Generate embeddings
            logging.info('Loading embedding model')
            encoder_name = 'Alibaba-NLP/gte-Qwen2-1.5B-instruct'
            encoder = SentenceTransformer(encoder_name, trust_remote_code=True)

            logging.info('Generating embeddings')
            increment = 10
            resumes = df[self.properties['text_column_name']].values
            doc_embeddings = encoder.encode(resumes[:increment])
            for i in tqdm(range(increment, len(resumes)+increment-1, increment)):
                new_emb = encoder.encode(resumes[i:i+increment])
                if len(new_emb.shape) == 2:
                    doc_embeddings = np.append(doc_embeddings, new_emb, axis=0)
            cluster_df = pd.DataFrame(doc_embeddings)

            #Save embeddings
            logging.info('Saving embeddings')
            if 'text_embedding_path' in self.properties:
                cluster_df.to_csv(self.properties['text_embedding_path'])
        return cluster_df

    # Build clusters and send call to OpenAI agent for labels
    def run_clustering(self, worker, results):
        df = pd.DataFrame(results)
        exclude_columns = self.properties['exclude_columns'] + [self.properties['id_column']]
        df = self.preprocess_for_clustering(df, exclude_columns=exclude_columns)
        if self.properties['use_text_embeddings'] == "True":
            cluster_df = self.get_embeddings_df(df)
        else:
            if len(self.properties['exclude_columns']) > 0:
                cluster_df = df.drop(self.properties['exclude_columns']+[self.properties['id_column']], axis=1)
            else:
                cluster_df = df.drop(self.properties['id_column'], axis=1)
        self.cluster_df = cluster_df

        if self.properties['num_clusters'] == 'auto' and self.properties['auto_cluster_method'] == 'llm':
            # Generate several possible clusterings and have LLM choose
            cluster_descriptions = {}
            cluster_labels = []
            for num_clusters in self.properties['cluster_size_options']:
                model = KMeans(n_clusters = num_clusters, random_state=self.properties['random_seed']).fit(cluster_df)
                df['cluster_labels'] = model.labels_
                df['cluster_labels'] = df['cluster_labels'].map(int)

                analysis = self.cluster_analysis(df, 'cluster_labels', exclude_cols=exclude_columns)
                cluster_descriptions['Num Clusters = '+str(num_clusters)] = analysis
                cluster_labels.append(df['cluster_labels'].values)    
            
            self.cluster_labels = cluster_labels
            logging.info('Issuing OpenAI multilabel call')
            self.issue_agent_call(cluster_descriptions, worker, 'OPENAI_LABELERMULTI', ".OPENAI_RESULTS", "AUTO_CLUSTER_LABELS")
        else:
            if type(self.properties['num_clusters']) == type(1):
                model = KMeans(n_clusters = self.properties['num_clusters'], random_state=self.properties['random_seed']).fit(cluster_df)
                df['cluster_labels'] = model.labels_
            else: #Rank clusters by silhouette score
                    logging.info('Using silhouette score.')
                    highest_score = -1
                    best_labels = None
                    for num_clusters in self.properties['cluster_size_options']:
                        model = KMeans(n_clusters = num_clusters, random_state=self.properties['random_seed']).fit(cluster_df)
                        score = silhouette_score(cluster_df, model.labels_).mean()
                        logging.info(f'Num Clusters: {num_clusters}, Score: {score}')
                        if score >= highest_score:
                            highest_score = score
                            best_labels = model.labels_
                    df['cluster_labels'] = best_labels

            df['cluster_labels'] = df['cluster_labels'].map(int)
            analysis = self.cluster_analysis(df, 'cluster_labels', exclude_cols=exclude_columns)

            # Get cluster labels
            self.issue_agent_call(analysis, worker, 'OPENAI_LABELER', ".OPENAI_RESULTS", "CLUSTER_LABELS")

        # Save data
        self.df = df

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        logging.info('-------------------------------------------')
        logging.info('-------------------------------------------')
        logging.info('-------------------------------------------')
        logging.info('-------------------------------------------')
        logging.info('Entering processor')
        logging.info(input)

        if "random_seed" not in self.properties:
            self.properties['random_seed'] = np.random.choice(500000)

        ##### Upon USER input text
        if input == "DEFAULT":
            logging.info('Default response found')
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

                # Parse response for cluster label mapping
                match = re.search(r'\{.*\}', data, re.DOTALL).group()
                cluster_label_mapping = json.loads(match)

                if self.properties['num_clusters'] == 'auto' and self.properties['auto_cluster_method'] == 'llm':
                    self.df['cluster_labels'] = self.cluster_labels[self.properties['cluster_size_options'].index(len(cluster_label_mapping))]

                self.df['cluster_labels_names'] = list(map(cluster_label_mapping.get, self.df['cluster_labels'].astype('str')))

                analysis = self.cluster_analysis(self.df, 'cluster_labels_names', ['cluster_labels'])

                # Show results to user
                logging.info(analysis)
                self.display_cluster_summaries(worker, analysis)
                if self.properties['create_visualization']:
                    self.create_visualization(worker, self.df)

                #Temporary solution for Kevin
                if self.properties['save_id_cluster_mapping']:
                    self.df[['job_seeker_id', 'cluster_labels_names']].to_csv('/blue_data/data/cluster_mapping.csv')
                    with open('/blue_data/data/cluster_distinctive_features.json', 'w', encoding='utf-8') as f:
                        json.dump(analysis, f, ensure_ascii=False, indent=4)
                    with open('/blue_data/data/cluster_distinctive_features.csv', 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['Cluster Label', 'Cluster Size', 'Feature Name', 'Feature Presence'])
                        for cluster_label, cluster_data in analysis.items():
                            for feature_name, feature_presence in cluster_data['distinctive_features'].items():
                                writer.writerow([cluster_label, cluster_data['cluster_size'], feature_name, feature_presence])

                self.issue_agent_call(json.dumps(analysis), worker, 'OPENAI_SUMMARIZER', ".SUMMARIZER_RESULTS", "CLUSTER_SUMMARIZATION")

            else:
                logging.info('OpenAI response not found')
        
        elif input == "SUMMARIZER_RESULTS":
            if message.isData():
                logging.info("Summarization results")
                stream = message.getStream()
                data = message.getData()
                logging.info(data)
                self.write_to_new_stream(worker, data, "TEXT")
            else:
                logging.info('Summarizer response not found')

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
