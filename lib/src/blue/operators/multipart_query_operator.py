###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer, default_attributes_validator
from blue.operators.registry import OperatorRegistry
from blue.operators.operator_discover import operator_discover_operator_function, operator_discover_operator_validator
from blue.data.pipeline import DataPipeline, Status

###############
### Multipart Query Operator


def multipart_query_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    # TODO:
    return [[]]


def multipart_query_operator_refiner(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:

    plans = input_data
    pipelines = []

    for plan in plans:
        # create pipeline for each alternative set
        pipeline = DataPipeline(properties=properties)

        ctes = plan
        # discover, query, create table, and insert for each cte
        failed = False

        ## build plan
        # input
        input_node = pipeline.define_input(value=[[]], properties=properties)
        # output
        output_node = pipeline.define_output(properties=properties)
        for cte in ctes:
            name = cte['name'] if 'name' in cte else None
            description = cte['description'] if 'description' in cte else None
            sql = cte['sql'] if 'sql' in cte else None
            table = cte['table'] if 'table' in cte else None
            columns = cte['columns'] if 'columns' in cte else None
            dependency = cte['dependency'] if 'dependency' in cte else None

            # fail
            if name is None or description is None or sql is None or table is None or columns is None or dependency is None:
                failed = True
                break

            # data discover
            data_discovery_attributes = {"search_query": description}
            data_discovery_node = pipeline.define_operator("/server/blue_ray/operator/data_discover", attributes=data_discovery_attributes, properties=properties)

            # nl2q
            # create table
            # insert table

            ## connections
            pipeline.connect_nodes(input_node, data_discovery_node)
            pipeline.connect_nodes(data_discovery_node, output_node)

        if failed:
            continue

        # add to pipelines
        pipelines.append(pipeline.to_dict())

    return pipelines


def multipart_query_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain multipart query operator output."""
    multipart_query_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"multipart query orchestarted the execution of...",
    }
    return multipart_query_explanation


###############
### MultipartQueryOperator
#
class MultipartQueryOperator(Operator):
    """
    multipart query operator orchestrates the execution of multi-part query, starting with data discovery, and exectution.
    """

    PROPERTIES = {
        "tool_type": "operator",
        "platform.name": "default",
        "operator_registry.name": "default",
    }

    name = "multipart_query"
    description = "Orchestrates the execution of multi-part query, starting with data discovery, and exectution"
    default_attributes = {}

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=multipart_query_operator_function,
            description=description or self.description,
            properties=properties or self.PROPERTIES,
            validator=default_attributes_validator,
            explainer=multipart_query_operator_explainer,
            refiner=multipart_query_operator_refiner,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # refine
        self.properties["refine"] = True


###########
### Helper functions
