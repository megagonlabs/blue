###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/platform/')


######
import time
import argparse
import logging
import time
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils

import itertools
from tqdm import tqdm

###### Backend, Databases
import redis
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

#######
import numpy as np
from sentence_transformers import SentenceTransformer

###### Blue
from registry import Registry


class ModelRegistry(Registry):
    def __init__(self, name="MODEL_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ###### initialization

    def _initialize_properties(self):
        super()._initialize_properties()

    ######### model
    def add_model(self, model, created_by, description="", properties={}, rebuild=False):
        super().register_record(model, "model", "/", created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_model(self, model, description="", icon=None, properties={}, rebuild=False):
        super().update_record(model, "model", "/", description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_model(self, model, rebuild=False):
        record = self.get_model(model)
        super().deregister(record, rebuild=rebuild)

    def get_model(self, model):
        return super().get_record(model, '/')

    def get_model_description(self, model):
        return super().get_record_description(model, '/')

    def set_model_description(self, model, description, rebuild=False):
        super().set_record_description(model, '/', description, rebuild=rebuild)

    # model properties
    def get_model_properties(self, model):
        return super().get_record_properties(model, '/')

    def get_model_property(self, model, key):
        return super().get_record_property(model, '/', key)

    def set_model_property(self, model, key, value, rebuild=False):
        super().set_record_property(model, '/', key, value, rebuild=rebuild)

    def delete_model_property(self, model, key, rebuild=False):
        super().delete_record_property(model, '/', key, rebuild=rebuild)

    # model location (part of properties)
    def get_model_location(self, model):
        return self.get_model_property(model, 'location')

    def set_model_location(self, model, location, rebuild=False):
        self.set_model_property(model, 'location', location, rebuild=rebuild)

    ### model perf
    # performance is stored hiearchically, by metric, metric+task, metric+task+dataset
    # e.g.
    #
    # "performance": {
    #     "macro": 0.8,
    #     "_metrics": {
    #       "latency": {
    #         "macro": 10
    #       },
    #       "accuracy": {
    #         "macro": 0.8,
    #         "_tasks": {
    #           "document_similarity": {
    #             "macro": 0.8,
    #             "_datasets": {
    #               "wikisec-base": 0.8042,
    #               "wikisec-large": 0.8078
    #             }
    #           }
    #         }
    #       },
    #       "cost": {
    #         "macro": 200
    #       }
    #     }
    #   }
    #
    #  Note: macro numbers are automatically calculated using macro metric calculation
    #  i.e. unweighted average, across all tasks, datasets, etc.
    def get_model_performance(self, model, metric=None, task=None, dataset=None, details=False):
        performance = self.get_model_property(model, 'performance')
        results = {}
        if metric is None:  
            if "macro" in performance:
                if details:
                    return performance
                else:
                    return performance["macro"]
            else:
                return None
        else:
            metrics = performance["_metrics"]
            if metric in metrics:
                metric_performance = metrics[metric]
                if task is None:
                    if "macro" in metric_performance:
                        if details:
                            return metric_performance
                        else:
                            return metric_performance["macro"]
                    else:
                        return results
                else:
                    tasks = metric_performance["_tasks"]
                    if task in tasks:
                        task_metric_performance = tasks[task]
                        if dataset is None:
                            if "macro" in task_metric_performance:
                                if details:
                                    return task_metric_performance
                                else:
                                    return task_metric_performance["macro"]
                            else:
                                return None
                        else:
                            datasets = task_metric_performance["_datasets"]
                            if dataset in datasets:
                                dataset_task_metric_performance = datasets[dataset]
                                return dataset_task_metric_performance
                            else:
                                return None
                    else:
                        return None

            else:
                return None


    def set_model_performance(self, model, value, metric=None, task=None, dataset=None):
        performance = self.get_model_property(model, 'performance')
        self._set_model_performance(model, value, performance, metric=metric, task=task, dataset=dataset)

    def _set_model_performance(self, model, value, performance, metric=None, task=None, dataset=None):
        # check if performance data exists
        if performance is None:
            # no performance data, initialize
            self.set_model_property(model, 'performance', {"macro": -1, "_metrics": {}})
            # redo
            self.set_model_performance(self, model, value, metric=metric, task=task, dataset=dataset)

        if metric is None:
            # set macro value
            self.set_model_property(model, 'performance.macro', value)
        else:
            metrics = performance["_metrics"]

            # check if metric performance data exists
            if metric not in metrics:
                # no metric performance data, initialize
                self.set_model_property(model, 'performance._metrics.' + metric, {"macro": -1, "_tasks": {}})
                # redo
                self.set_model_performance(self, model, value, metric=metric, task=task, dataset=dataset)

            # metric performance data
            metric_performance = metrics[metric]
                        
            if task is None:
                # set macro value for metric
                self.set_model_property(model, 'performance._metrics.' + metric + '.macro', value)
                ### TODO: combine multiple metrics performances to compute overall model performance, given multiple metrics
                # issue: #327
                # simple macro won't work here, need to align metrics (range, direction)
            else:
                tasks = metric_performance["_tasks"]

                # check if task metric performance data exists
                if task not in tasks:
                    # no task metric performance data exists, initialize
                    self.set_model_property(model, 'performance._metrics.' + metric + '._tasks.' + task, {"macro": -1, "_datasets": {}})
                    # redo
                    self.set_model_performance(self, model, value, metric=metric, task=task, dataset=dataset)

                # task metric performance data
                task_metric_performance = tasks[task]

                if dataset is None:
                    # set macro value for task, metric
                    self.set_model_property('performance._metrics.' + metric + '._tasks.' + task + '.macro', value)
                    ### combine multiple tasks performances to compute overall model performance for metric, given multiple tasks
                    # do simple macro stats
                    p_sum = 0.0
                    p_count = 0
                    for task in tasks:
                        task_metric_performance = tasks[task]
                        p = task_metric_performance["macro"]
                        p_sum = p_sum + p
                        p_count = p_count + 1
                    p_macro = p_sum / p_count
                    self.set_model_performance(model, p_macro, metric=metric, task=None, dataset=None)
                else:
                    datasets = task_metric_performance["_datasets"]
                    # set value
                    self.set_model_property('performance._metrics.' + metric + '._tasks.' + task + '._datasets.' + dataset, value)
                    ### combine multiple dataset performances to compute overall model performance for task, given multiple datasets
                    # do simple macro stats
                    p_sum = 0.0
                    p_count = 0
                    for dataset in datasets:
                        dataset_task_metric_performance = datasets[dataset]
                        p = dataset_task_metric_performance
                        p_sum = p_sum + p
                        p_count = p_count + 1
                    p_macro = p_sum / p_count
                    self.set_model_performance(model, p_macro, metric=metric, task=task, dataset=None)




#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='MODEL_REGISTRY', help='name of the registry')
    parser.add_argument('--id', type=str, default='default', help='id of the registry')
    parser.add_argument('--sid', type=str, help='short id (sid) of the registry')
    parser.add_argument('--cid', type=str, help='canonical id (cid) of the registry')
    parser.add_argument('--prefix', type=str, help='prefix for the canonical id of the registry')
    parser.add_argument('--suffix', type=str, help='suffix for the canonical id of the registry')
    parser.add_argument('--properties', type=str, help='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, help='log level')
    parser.add_argument('--add', type=str, default=None, help='json array of models to be add to the registry')
    parser.add_argument('--update', type=str, default=None, help='json array of models to be updated in the registry')
    parser.add_argument('--remove', type=str, default=None, help='json array of models names to be removed')
    parser.add_argument('--search', type=str, default=None, help='search registry with keywords')
    parser.add_argument('--type', type=str, default=None, help='search registry limited to model metadata type [model, input, output]')
    parser.add_argument('--scope', type=str, default=None, help='limit to scope')
    parser.add_argument('--page', type=int, default=0, help='search result page, default 0')
    parser.add_argument('--page_size', type=int, default=5, help='search result page size, default 5')
    parser.add_argument('--list', type=bool, default=False, action=argparse.BooleanOptionalAction, help='list models in the registry')
    parser.add_argument('--approximate', type=bool, default=False, action=argparse.BooleanOptionalAction, help='use approximate (embeddings) search')
    parser.add_argument('--hybrid', type=bool, default=False, action=argparse.BooleanOptionalAction, help='use hybrid (keyword and approximate) search')

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    print(args)
    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    # create a registry
    registry = ModelRegistry(name=args.name, id=args.id, sid=args.sid, cid=args.cid, prefix=args.prefix, suffix=args.suffix, properties=properties)

    #### LIST
    if args.list:
        # list the records in registry
        results = registry.list_records()
        logging.info(results)

    #### ADD
    if args.add:
        registry.loads(args.add)

        # list the registryrecords = json
        results = registry.list_records()
        logging.info(results)
        logging.info(registry.get_contents())

    #### UPDATE
    if args.update:
        records = json.loads(args.update)
        print(records)
        for record in records:
            registry.update_record_json(record)

        # index registry
        registry.build_index()

        # list the registry
        results = registry.list_records()
        logging.info(results)

    #### REMOVE
    if args.remove:
        records = json.loads(args.remove)
        print(records)
        for record in records:
            # deregister
            registry.deregister(record, rebuild=True)

        # list the registry
        results = registry.list_records()
        logging.info(results)

    #### SEARCH
    if args.search:
        keywords = args.search

        # search the registry
        results = registry.search_records(keywords, type=args.type, scope=args.scope, approximate=args.approximate, hybrid=args.hybrid, page=args.page, page_size=args.page_size)

        logging.info(json.dumps(results, indent=4))
