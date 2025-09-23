###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer, default_attributes_validator
from blue.operators.registry import OperatorRegistry
from blue.operators.operator_discover import operator_discover_operator_function, operator_discover_operator_validator
from blue.data.pipeline import DataPipeline, Status

###############
### NL2Query Router Operator


def nl2query_router_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    # TODO:
    return [[]]


def nl2query_router_operator_refiner(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:

    pipelines = []

    if len(input_data) == 0:
        return pipelines

    sources = input_data[0]

    query = attributes['search_query']
    columns = attributes['columns']
    execute_query = attributes['execute_query']

    for source in sources:
        source_name = source['name']

        # create pipeline for each source
        pipeline = DataPipeline(properties=properties)

        # check source protocol
        if 'properties' not in source:
            continue
        properties = source['properties']
        if 'connection' not in properties:
            continue
        connection = properties['connection']
        if 'protocol' not in connection:
            continue
        protocol = connection['protocol']

        # input
        input_node = pipeline.define_input(value=None)

        # output
        output_node = pipeline.define_output(properties={})

        # set plan input / output
        pipeline.set_plan_input(input_node)
        pipeline.set_plan_output(output_node)

        route_node = None
        if protocol == "openai":
            nl2llm_attributes = {"query": query, "attrs": columns}
            route_node = nl2lm_node = pipeline.define_operator("/server/blue_ray/operator/nl2llm", attributes=nl2llm_attributes, properties={})
        elif protocol == "postgres" or protocol == "mysql" or protocol == "sqlite":
            nl2sql_attributes = {"question": query, "protocol": protocol, "source": source_name, "execute_query": execute_query}
            # TODO: add attr_names (#1205)
            route_node = nl2sql_node = pipeline.define_operator("/server/blue_ray/operator/nl2sql", attributes=nl2sql_attributes, properties={})
        else:
            # TODO: support other protocols
            continue

        ## connections
        pipeline.connect_nodes(input_node, route_node)
        pipeline.connect_nodes(route_node, output_node)

        # add to pipelines
        pipelines.append(pipeline.to_dict())

    return pipelines


def nl2query_router_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain nl2query router operator output."""
    nl2query_router_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"routes the execution of query to...",
    }
    return nl2query_router_explanation


###############
### NL2QueryRouterOperator
#
class NL2QueryRouterOperator(Operator):
    """
    nl2query router operator refines to the right nl2q operator based on source.
    """

    PROPERTIES = {}

    name = "nl2query_router"
    description = "Routees the execution of query, based on source"
    default_attributes = {}

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=nl2query_router_operator_function,
            description=description or self.description,
            properties=properties,
            validator=default_attributes_validator,
            explainer=nl2query_router_operator_explainer,
            refiner=nl2query_router_operator_refiner,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # refine
        self.properties["refine"] = True


###########
### Helper functions
