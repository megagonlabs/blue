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
    plans = []

    return plans


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
