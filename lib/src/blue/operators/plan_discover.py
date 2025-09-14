###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.operators.registry import OperatorRegistry
from blue.operators.operator_discover import operator_discover_operator_function, operator_discover_operator_validator
from blue.data.pipeline import DataPipeline, Status

###############
### Operator Discover Operator


def plan_discover_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    # TODO:
    return [[]]


def plan_discover_operator_refiner(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    plans = []
    # perform search for top-level operators
    result = operator_discover_operator_function(input_data, attributes=attributes, properties=properties)
    results = result[0]

    if results is None:
        return plans

    # TODO: prune plans

    # transform top-level operators as single-node plans

    for index, result in enumerate(results):
        operator_path = result['path']
        p = DataPipeline()
        # create a plan with input, operator from search, and output
        i = p.define_input(value=input_data)
        i.set_data("status", str(Status.EXECUTED))
        r = p.define_output()
        o = p.define_operator(operator_path)
        o.set_data("status", str(Status.INITED))
        p.connect_nodes(i, o)
        p.connect_nodes(o, r)
        plans.append(p.get_data())
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
    plan discover operator that searches for top-level operators as plan starters
    """

    PROPERTIES = {}

    name = "plan_discover"
    description = "Discovers plans using the operator registry to search for top-level operators as plan starters"
    default_attributes = {
        "search_query": {"type": "str", "description": "Text to search for in operator names and descriptions", "required": True, "default": ""},
        "approximate": {"type": "bool", "description": "Whether to use approximate (vector) search", "required": True, "default": True},
        "hybrid": {"type": "bool", "description": "Whether to use hybrid search (text + vector)", "required": False, "default": False},
        "page": {"type": "int", "description": "Page number for pagination", "required": False, "default": 0},
        "page_size": {"type": "int", "description": "Number of results per page (default: 10, max: 100)", "required": False, "default": 10},
        "include_metadata": {"type": "bool", "description": "Whether to include metadata in results (description and properties always included)", "required": False, "default": False},
        "threshold": {"type": "float", "description": "Similarity threshold for filtering results (0.0-1.0, lower = more similar, only applies to approximate/hybrid search)", "required": False, "default": 0.5},
        "progressive_pagination": {"type": "bool", "description": "Whether to use progressive pagination for approximate/hybrid search (searches all pages until threshold exceeded)", "required": False, "default": False},
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
