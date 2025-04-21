###### Blue
from blue.registry import Registry

class ModelRegistry(Registry):
    def __init__(self, name="MODEL_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, type="model", id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

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
        return super().get_record(model, 'model', '/')

    def get_model_description(self, model):
        return super().get_record_description(model, 'model', '/')

    def set_model_description(self, model, description, rebuild=False):
        super().set_record_description(model, 'model', '/', description, rebuild=rebuild)

    # model properties
    def get_model_properties(self, model):
        return super().get_record_properties(model, 'model', '/')

    def get_model_property(self, model, key):
        return super().get_record_property(model, 'model', '/', key)

    def set_model_property(self, model, key, value, rebuild=False):
        super().set_record_property(model, 'model', '/', key, value, rebuild=rebuild)

    def delete_model_property(self, model, key, rebuild=False):
        super().delete_record_property(model, 'model', '/', key, rebuild=rebuild)

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