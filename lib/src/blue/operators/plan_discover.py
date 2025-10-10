###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.operators.registry import OperatorRegistry
from blue.operators.operator_discover import operator_discover_operator_function, operator_discover_operator_validator
from blue.data.pipeline import DataPipeline, Status
from blue.utils import json_utils

###############
### Operator Discover Operator


def plan_discover_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    # TODO:
    return [[]]


def plan_discover_operator_refiner(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    plans = []
    ## discover plans
    # simply use operator search
    task = attributes['task']
    data = attributes['data']
    limit = attributes.get('limit', -1)

    ### use operator discover to find seed operator t
    # modify attributes for operator discover operator
    opeator_discover_properties = {}
    opeator_discover_properties = json_utils.merge_json(opeator_discover_properties, attributes)
    del opeator_discover_properties['task']
    opeator_discover_properties['search_query'] = task

    result = operator_discover_operator_function(input_data, attributes=opeator_discover_properties, properties=properties)
    results = result[0]

    if results is None:
        return plans

    # TODO: prune plans

    # transform top-level operators as single-node plans
    for index, result in enumerate(results):
        operator_path = result['path']

        # create a plan with search results
        p = DataPipeline()

        # input / output
        i = p.define_input(value=None)
        r = p.define_output()
        # set plan input / output
        p.set_plan_input(i)
        p.set_plan_output(r)

        # operator from search results
        o = p.define_operator(operator_path)
        o.set_data("status", str(Status.INITED))
        p.connect_nodes(i, o)
        p.connect_nodes(o, r)
        plans.append(p.get_data())

    # limit results
    if limit >= 0:
        return plans[:limit]
    else:
        return plans


def plan_discover_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate operator discover operator attributes."""
    return operator_discover_operator_validator(input_data, attributes=attributes, properties=properties)


def plan_discover_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain plan discover operator output."""
    plan_discover_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"plan discover operator searched for top-level operators with query '{attributes.get('search_query', '')}' and returned {len(output[0]) if output and len(output) > 0 else 0} results.",
    }
    return plan_discover_explanation


###############
### PlanDiscoverOperator
#
class PlanDiscoverOperator(Operator):
    """
    Plan discover operator that searches for top-level operators as plan starters, given a task and data

    Attributes:
    ----------
    | Name                    | Type  | Required | Default | Description                                                                                       |
    |-------------------------|-------|----------|---------|---------------------------------------------------------------------------------------------------|
    | `task`                  | str   | :fontawesome-solid-circle-check: {.green-check}     | ""      | Task to discover plans/operators                                                                 |
    | `data`                  | str   | :fontawesome-solid-circle-check: {.green-check}     | ""      | Data to operate the task on                                                                      |
    | `approximate`           | bool  | :fontawesome-solid-circle-check: {.green-check}     | True    | Whether to use approximate (vector) search                                                      |
    | `hybrid`                | bool  |     | False   | Whether to use hybrid search (text + vector)                                                   |
    | `limit`                 | int   |     | -1      | Max number of results to return (-1 for unlimited)                                             |
    | `page`                  | int   |     | 0       | Page number for pagination                                                                      |
    | `page_size`             | int   |     | 10      | Number of results per page (default: 10, max: 100)                                             |
    | `include_metadata`      | bool  |     | False   | Whether to include metadata in results (description and properties always included)            |
    | `threshold`             | float |     | 0.5     | Similarity threshold for filtering results (0.0-1.0, lower = more similar; applies to approximate/hybrid search) |
    | `progressive_pagination`| bool  |     | False   | Whether to use progressive pagination for approximate/hybrid search (searches all pages until threshold exceeded) |
    """

    PROPERTIES = {}

    name = "plan_discover"
    description = "Discovers plans using the operator registry to search for top-level operators as plan starters"
    default_attributes = {
        "task": {"type": "str", "description": "Task to discover plans/operators", "required": True, "default": ""},
        "data": {"type": "str", "description": "Data to operate the task on", "required": True, "default": ""},
        "approximate": {"type": "bool", "description": "Whether to use approximate (vector) search", "required": True, "default": True},
        "hybrid": {"type": "bool", "description": "Whether to use hybrid search (text + vector)", "required": False, "default": False},
        "limit": {"type": "int", "description": "Max number of results to return (-1, unlimited)", "required": False, "default": -1},
        "page": {"type": "int", "description": "Page number for pagination", "required": False, "default": 0},
        "page_size": {"type": "int", "description": "Number of results per page (default: 10, max: 100)", "required": False, "default": 10},
        "include_metadata": {"type": "bool", "description": "Whether to include metadata in results (description and properties always included)", "required": False, "default": False},
        "threshold": {
            "type": "float",
            "description": "Similarity threshold for filtering results (0.0-1.0, lower = more similar, only applies to approximate/hybrid search)",
            "required": False,
            "default": 0.5,
        },
        "progressive_pagination": {
            "type": "bool",
            "description": "Whether to use progressive pagination for approximate/hybrid search (searches all pages until threshold exceeded)",
            "required": False,
            "default": False,
        },
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=plan_discover_operator_function,
            description=description or self.description,
            properties=properties,
            validator=plan_discover_operator_validator,
            explainer=plan_discover_operator_explainer,
            refiner=plan_discover_operator_refiner,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # refine
        self.properties["refine"] = True


###########
### Helper functions
