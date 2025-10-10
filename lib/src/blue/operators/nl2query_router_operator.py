###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer, default_attributes_validator
from blue.operators.registry import OperatorRegistry
from blue.operators.operator_discover import operator_discover_operator_function, operator_discover_operator_validator
from blue.data.pipeline import DataPipeline, Status

###############
### NL2Query Router Operator


def nl2query_router_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Route the execution of query to the right nl2q operator based on source.

    NL2QueryRouterOperator only does plan refinement. This function simply returns empty output.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), uses first data source as base.
        attributes: Dictionary containing operator attributes including search_query, columns, execute_query, protocol.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        Empty list.
    """
    return [[]]


def nl2query_router_operator_refiner(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Refine the nl2query router plan by constructing a data pipeline for each source or collection.

    Depending on the protocol of the source/collection, it routes to either nl2llm or nl2sql operator, and may do additional data discovery.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), each array represents a source or collection to route the query to.
        attributes: Dictionary containing operator attributes including search_query, columns, execute_query, protocol.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List of data pipelines (as dictionaries) representing the refined nl2query router plans.
    """
    pipelines = []

    if len(input_data) == 0:
        return pipelines

    elements = input_data[0]

    query = attributes.get('search_query')
    columns = attributes.get('columns')
    execute_query = attributes.get('execute_query', True)
    protocol = attributes.get('protocol', '')

    for element in elements:
        name = element['name']
        type = element['type']
        scope = element['scope']

        parsed = parse_scope(scope)

        # create pipeline for each source
        pipeline = DataPipeline(properties=properties)

        # input
        input_node = pipeline.define_input(value=None)

        # output
        output_node = pipeline.define_output(properties={})

        # set plan input / output
        pipeline.set_plan_input(input_node)
        pipeline.set_plan_output(output_node)

        if type == "source":
            # route based on source
            source = element
            # source name
            source_name = source['name']
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

            if protocol == "openai":
                nl2llm_attributes = {"source": source_name, "query": query, "attrs": columns}
                # TODO: need to pass specific source to the nl2lmm as well (if there are multiple )
                nl2llm_node = pipeline.define_operator("/server/blue_ray/operator/nl2llm", attributes=nl2llm_attributes, properties={})

                # directly refine to nl2llm
                pipeline.connect_nodes(input_node, nl2llm_node)
                pipeline.connect_nodes(nl2llm_node, output_node)

            elif protocol == "postgres" or protocol == "mysql" or protocol == "sqlite":
                # do further data discovery and route again
                data_discovery_attributes = {
                    "source": source_name,
                    "scope": "/source/" + source_name,
                    "search_query": query,
                    "approximate": True,
                    "concept_type": 'collection',
                    'limit': 1,
                    'use_hierarchical_search': True,
                }
                data_discovery_node = pipeline.define_operator("/server/blue_ray/operator/data_discover", attributes=data_discovery_attributes, properties={})

                nl2query_router_attributes = {"search_query": query, "protocol": protocol, "execute_query": True, "columns": columns}
                nl2query_router_node = pipeline.define_operator("/server/blue_ray/operator/nl2query_router", attributes=nl2query_router_attributes, properties={})

                # firtst data discover then nl2query_router
                pipeline.connect_nodes(input_node, data_discovery_node)
                pipeline.connect_nodes(data_discovery_node, nl2query_router_node)
                pipeline.connect_nodes(nl2query_router_node, output_node)
            else:
                # TODO: support other protocols
                continue

        elif type == "collection":
            source = parsed['source']
            database = parsed['database']
            collection = name

            if protocol == "openai":
                nl2llm_attributes = {"query": query, "attrs": columns}
                nl2llm_node = pipeline.define_operator("/server/blue_ray/operator/nl2llm", attributes=nl2llm_attributes, properties={})

                # directly refine to nl2llm
                pipeline.connect_nodes(input_node, nl2llm_node)
                pipeline.connect_nodes(nl2llm_node, output_node)

            elif protocol == "postgres" or protocol == "mysql" or protocol == "sqlite":
                attr_names = [column['name'] for column in columns]
                nl2sql_attributes = {
                    "question": query,
                    "protocol": protocol,
                    "source": source,
                    "database": database,
                    "collection": collection,
                    "attr_names": attr_names,
                    "execute_query": execute_query,
                }
                nl2sql_node = pipeline.define_operator("/server/blue_ray/operator/nl2sql", attributes=nl2sql_attributes, properties={})

                # directly refine to nl2sql
                pipeline.connect_nodes(input_node, nl2sql_node)
                pipeline.connect_nodes(nl2sql_node, output_node)

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
    NL2Query router operator refines to the right nl2q operator based on source.

    Attributes:
    ----------
    | Name           | Type        | Required | Default | Description                                                |
    |----------------|------------|---------|---------|------------------------------------------------------------|
    | `search_query`    | str        | :fontawesome-solid-circle-check: {.green-check}    | -       | Natural language query to process                          |
    | `columns`         | list[dict] |    | []      | List of attribute specifications (dicts with name and optional type) |
    | `execute_query`   | bool       |    | True    | Whether to execute query or just translate NL to query    |
    | `protocol`        | str        |    | ""      | Protocol of the source                                     |

    """

    PROPERTIES = {}

    name = "nl2query_router"
    description = "Routees the execution of query, based on source"
    default_attributes = {
        "search_query": {"type": "str", "description": "Natural language query to process", "required": True},
        "columns": {"type": "list[dict]", "description": "List of attribute specifications (dicts with name and optional type)", "required": False, "default": []},
        "execute_query": {"type": "bool", "description": "Whether to execute query or just translate nl to query", "required": False, "default": True},
        "protocol": {"type": "str", "description": "Protocol of the source", "required": False, "default": ""},
    }

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


def parse_scope(scope):
    pa = scope.split("/")[1:]
    o = {}
    keys = pa[::2]
    if len(keys) <= 1:
        return o
    values = pa[1:][::2]
    for i, key in enumerate(keys):
        o[key] = values[i]
    return o
