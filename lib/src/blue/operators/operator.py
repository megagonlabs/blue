###### Parsers, Formats, Utils
from typing import List, Dict, Any, Callable, Union, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError
import copy
import json

import traceback
import logging

###### Blue
from blue.tools.tool import Tool
from blue.utils import json_utils, tool_utils, uuid_utils
from blue.utils.type_utils import string_to_python_type, create_pydantic_model, validate_parameter_type
from blue.data.pipeline import DataPipeline, Status
from blue.utils import log_utils

###############
### Operator


def default_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Default function for operator. It should be overridden by each operator.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records to process.
        attributes: Dictionary containing operator-specific parameters.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        Empty list as default implementation.
    """
    return []


def default_operator_refiner(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Default refiner for operator. It should be overridden by each operator.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records to process.
        attributes: Dictionary containing operator-specific parameters.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        Empty list as default implementation.
    """
    return []


def default_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Default validator for operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    try:
        return default_attributes_validator(attributes, properties)
    except Exception as e:
        # validation error
        return False


def default_attributes_validator(attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate actual attributes (attributes) using the attribute definitions in properties.

    Parameters:
        attributes: Dictionary containing actual attribute values to validate.
        properties: Optional properties dictionary containing attribute definitions. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    # Need to get the attributes definition and validation error handling from properties
    logging.debug("Validating attributes...")
    if properties is None:
        properties = {}
    attributes_def = properties.get("attributes", {})
    validation_error_handling = properties.get("validation_error_handling", "fail")
    # Validate required attributes
    for attrib_name, attrib_def in attributes_def.items():
        # check if required attribute is present
        required = attrib_def.get("required", False)
        if required and attrib_name not in attributes:
            logging.error("Failed for " + attrib_name)
            return False
        # validate attribute type
        if attrib_name in attributes:
            attrib_value = attributes[attrib_name]
            attrib_type = attrib_def.get("type")
            if attrib_type:
                try:
                    if not validate_parameter_type(attrib_value, attrib_type):
                        logging.error("Failed type for " + attrib_name)
                        return False
                except Exception as e:
                    # System failure in validation - handle based on configuration
                    error_msg = f"attribute validation system error for '{attrib_name}': {e}"
                    if validation_error_handling == "fail":
                        # raise validation error
                        logging.error(error_msg)
                        raise e
                    elif validation_error_handling == "log":
                        logging.error(error_msg)
                        logging.error(error_msg)
                        logging.error(attrib_name)
                        return False
                    else:  # skip
                        # Continue with validation (treat as if validation passed)
                        logging.error(error_msg)
                        logging.error(attrib_name)

    return True


def default_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Default explainer for operator output.

    Parameters:
        output: The output result from the operator execution.
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation with statistics.
    """
    total_input_records = sum(len(data) for data in input_data)
    output_count = len(output) if isinstance(output, list) else 1

    explanation = {
        "output": output,  # maybe not needed
        "num_input_data": len(input_data),
        "num_input_records": total_input_records,
        "num_input_records_per_data": [len(data) for data in input_data],
        "num_output_data": len(output),
        "num_output_records": output_count,
        "transformation_ratio": output_count / total_input_records if total_input_records > 0 else 0,
        "attributes": attributes,
    }
    return explanation


class Operator(Tool):
    """Base class for all operators in the Blue framework.

    Data in operator scope refers to JSON array of records (list of dictionaries) in Blue.
    Operator is a specialized Tool to perform data operations in Blue.
    Input data for operators: always expects multiple Data as [data_1, data_2, ...] (list of lists of dictionaries)
    Output data for operators: same as input data, always returns a list of JSON array of records. If there is only one data returned, it will return a list with one element (data).

    Parameters:
        name: Name of the operator.
        function: The operator function to execute. Defaults to default_operator_function.
        description: Description of the operator. Defaults to None.
        properties: Properties dictionary for the operator. Defaults to None.
        validator: Validation function for operator attributes. Defaults to default_operator_validator.
        explainer: Explanation function for operator output. Defaults to default_operator_explainer.
        refiner: Refinement function for operator planning. Defaults to default_operator_refiner.
    """

    PROPERTIES = {}

    def __init__(
        self, name: str, function: Callable = None, description: str = None, properties: Dict[str, Any] = None, validator: Callable = None, explainer: Callable = None, refiner: Callable = None
    ):
        """Initialize the Operator.

        Parameters:
            name: Name of the operator.
            function: The operator function to execute. Defaults to default_operator_function.
            description: Description of the operator. Defaults to None.
            properties: Properties dictionary for the operator. Defaults to None.
            validator: Validation function for operator attributes. Defaults to default_operator_validator.
            explainer: Explanation function for operator output. Defaults to default_operator_explainer.
            refiner (callable): Refinement function for operator planning. Defaults to default_operator_refiner.
        """
        if function is None:
            function = default_operator_function
        if validator is None:
            validator = default_operator_validator
        if explainer is None:
            explainer = default_operator_explainer
        if refiner is None:
            refiner = default_operator_refiner
        self.refiner = refiner

        super().__init__(name, function, description=description, properties=properties, validator=validator, explainer=explainer)

    def _initialize_properties(self):
        super()._initialize_properties()

        # Tool type
        self.properties["tool_type"] = "operator"

        # Operator identification properties
        self.properties["validate_input"] = True
        self.properties["validate_output"] = True
        self.properties["validation_error_handling"] = "fail"  # fail, log, skip
        # Processing properties
        self.properties["max_records"] = None  # None means no limit
        self.properties["timeout"] = 300  # 5 minutes timeout

        # Error handling properties
        self.properties["error_handling"] = "skip"  # fail, log, skip
        self.properties["log_processing_stats"] = True

        # attribute definitions
        self.properties["attributes"] = {}

        # hyperparameter definitions
        self.properties["hyperparameters"] = {}

        # refine
        self.properties["refine"] = False

        # process default PROPERTIES
        for property in self.PROPERTIES:
            self.properties[property] = self.PROPERTIES[property]

    def _extract_signature(self):
        super()._extract_signature()

        # expand parameters with attribute metadata, in function signature attributes
        signature = self.properties['signature']

        if 'attributes' in signature['parameters']:
            attributes = signature['parameters']['attributes']
            attributes['properties'] = copy.deepcopy(self.properties["attributes"])
            for a in attributes['properties']:
                attribute = attributes['properties'][a]
                attribute['type'] = tool_utils.convert_type_string_to_mcp(attribute['type'])

    def get_attributes(self):
        """Get all operator attributes.

        Returns:
            (dict): Dictionary containing all operator attributes and their definitions.
        """
        return self.properties["attributes"]

    def update_attributes(self, attributes=None):
        """Update operator attributes with new definitions.

        Parameters:
            (dict, None): attributes: Dictionary of attribute definitions to update. Defaults to None.
        """
        if attributes is None:
            return

        # override
        for p in attributes:
            self.properties["attributes"][p] = attributes[p]

        # update signature with updated attributes
        self._extract_signature()

    def get_attribute(self, attribute):
        """Get a specific operator attribute definition.

        Parameters:
            attribute: Name of the attribute to retrieve.

        Returns:
            (dict, None): Dictionary containing the attribute definition, or None if not found.
        """
        attributes = self.get_attributes()
        if attribute in attributes:
            return attributes[attribute]
        return None

    def get_attribute_type(self, attribute):
        """Get the type of a specific operator attribute.

        Parameters:
            attribute: Name of the attribute.

        Returns:
            (str, None): String containing the attribute type, or None if not found.
        """
        attribute = self.get_attribute(attribute)
        if attribute:
            if 'type' in attribute:
                return attribute['type']
        return None

    def get_attribute_description(self, attribute):
        """Get the description of a specific operator attribute.

        Parameters:
            attribute: Name of the attribute.

        Returns:
            (str, None): String containing the attribute description, or None if not found.
        """
        attribute = self.get_attribute(attribute)
        if attribute:
            if 'description' in attribute:
                return attribute['description']
        return None

    def set_attribute_description(self, attribute, description):
        """Set the description of a specific operator attribute.

        Parameters:
            attribute: Name of the attribute.
            description (str): New description for the attribute.
        """
        attribute = self.get_attribute(attribute)
        if attribute:
            attribute['description'] = description
            # update signature with updated attributes
            self._extract_signature()
        return None

    def set_attribute_required(self, attribute, required):
        """Set whether a specific operator attribute is required.

        Parameters:
            attribute: Name of the attribute.
            required (bool): Boolean indicating if the attribute is required.
        """
        attribute = self.get_attribute(attribute)
        if attribute:
            attribute['required'] = required
            # update signature with updated attributes
            self._extract_signature()
        return None

    def set_attribute_hidden(self, attribute, hidden):
        """Set whether a specific operator attribute is hidden.

        Parameters:
            attribute: Name of the attribute.
            hidden: Boolean indicating if the attribute is hidden.
        """
        attribute = self.get_attribute(attribute)
        if attribute:
            attribute['hidden'] = hidden
            # update signature with updated attributes
            self._extract_signature()
        return None

    def is_attribute_required(self, attribute):
        """Check if a specific operator attribute is required.

        Parameters:
            attribute: Name of the attribute.

        Returns:
            Boolean indicating if the attribute is required, or None if not found.
        """
        attribute = self.get_attribute(attribute)
        if attribute:
            if 'required' in attribute:
                return attribute['required']
        return None

    def is_attribute_hidden(self, attribute):
        """Check if a specific operator attribute is hidden.

        Parameters:
            attribute: Name of the attribute.

        Returns:
            Boolean indicating if the attribute is hidden, or None if not found.
        """
        attribute = self.get_attribute(attribute)
        if attribute:
            if 'hidden' in attribute:
                return attribute['hidden']
        return None

    def get_hyperparameters(self):
        """Get all operator hyperparameters.

        Returns:
            Dictionary containing all operator hyperparameters.
        """
        return self.properties["hyperparameters"]

    def update_hyperparameters(self, hyperparameters=None):
        """Update operator hyperparameters with new values.

        Parameters:
            hyperparameters: Dictionary of hyperparameter values to update. Defaults to None.
        """
        if hyperparameters is None:
            return
        # override
        for p in hyperparameters:
            self.properties["hyperparameters"][p] = hyperparameters[p]

    ######### Seperation functions to let LLM or other caller know if it's an operator or a function
    @classmethod
    def is_operator(cls, function_or_operator) -> bool:
        """Check if a tool/operator is actually an operator.

        Parameters:
            function_or_operator: The object to check.

        Returns:
            True if the object is an operator, False otherwise.
        """
        if hasattr(function_or_operator, 'properties'):
            return function_or_operator.properties.get("tool_type") == "operator"
        return False

    @classmethod
    def get_tool_type(cls, function_or_operator) -> str:
        """Get the type of a function/operator.

        Parameters:
            function_or_operator: The object to check.

        Returns:
            String indicating the type: "operator" or "function".
        """
        if cls.is_operator(function_or_operator):
            return "operator"
        return "function"

    ######### class-method-based operator execution flow as optional version besides function based operator design
    # def execute_operator(self, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any] = {}) -> Dict[str, Any]:
    #     """
    #     Main entry point for operator execution.
    #     This method orchestrates the complete execution flow and returns a structured result.
    #     Parameters:
    #         input_data: List of data sources, each containing JSON array of records
    #         attributes: Operator-specific attribute values (actual values, not definitions)
    #     Returns:
    #         Dictionary containing result, error, and explanation
    #     """
    #     try:
    #         # Validate input_data
    #         if self.properties.get("validate_input", True) and not self._validate_input_data(input_data):
    #             return {
    #                 "operator": self.name,
    #                 "input_data": input_data,
    #                 "attributes": attributes or {},
    #                 "result": [],
    #                 "error": "Invalid input_data format",
    #                 "explain": {"error": "input_data must be a list of lists of dictionaries"},
    #             }

    #         # Validate attributes
    #         if not self.validator(attributes or {}):
    #             return {
    #                 "operator": self.name,
    #                 "input_data": input_data,
    #                 "attributes": attributes or {},
    #                 "result": [],
    #                 "error": "attribute validation failed",
    #                 "explain": {"error": "Invalid attributes provided"},
    #             }

    #         # Execute operator-specific logic
    #         result = self._execute_operator_logic(input_data, attributes or {})

    #         # Validate output data
    #         if self.properties.get("validate_output", True) and not self._validate_io_data(result):
    #             return {
    #                 "operator": self.name,
    #                 "input_data": input_data,
    #                 "attributes": attributes or {},
    #                 "result": result,
    #                 "error": "Invalid output data format",
    #                 "explain": {"error": "output_data must be a list of lists of dictionaries"},
    #             }

    #         # Generate explanation
    #         explanation = self.explainer(result, input_data, attributes or {})
    #         return {"operator": self.name, "input_data": input_data, "attributes": attributes or {}, "result": result, "error": None, "explain": explanation}

    #     except Exception as e:
    #         error_handling = self.properties.get("error_handling", "skip")

    #         if error_handling == "fail":
    #             raise e
    #         elif error_handling == "log":
    #             logging.error(f"Error in {self.name}, skipping: {str(e)}")
    #             return {"operator": self.name, "input_data": input_data, "attributes": attributes or {}, "result": [], "error": str(e), "explain": {"error": f"Execution failed: {str(e)}"}}
    #         else:  # skip
    #             logging.info(f"Error in {self.name}, skipping: {str(e)}")
    #             return {"operator": self.name, "input_data": input_data, "attributes": attributes or {}, "result": [], "error": str(e), "explain": {"error": f"Execution failed: {str(e)}"}}

    # def _validate_io_data(self, input_data: List[List[Dict[str, Any]]]) -> bool:
    #     """Validate input/output data format. It should be a list of lists of dictionaries."""
    #     if not isinstance(input_data, list):
    #         return False
    #     for data in input_data:
    #         if not isinstance(data, list):
    #             return False
    #         for item in data:
    #             if not isinstance(item, dict):
    #                 return False
    #     return True

    # def _execute_operator_logic(self, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
    #     """
    #     Execute the actual operator-specific logic.
    #     This method contains the core logic for each operator type.
    #     Operators should override this method with their specific implementation.
    #     Parameters:
    #         input_data: List of datas, each containing JSON array of records
    #         attributes: Operator-specific attribute values
    #     Returns:
    #         List of datas, each containing JSON array of records
    #     """
    #     # Default implementation: return the datas as they are
    #     # Subclasses MUST override this with their specific logic
    #     return input_data


###############
### DeclarativeOperator


def declarative_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Default function for declarative operator, simply passes execution to sub plans.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records to process.
        attributes: Dictionary containing operator-specific parameters.
        properties: Optional properties dictionary containing plan definitions. Defaults to None.

    Returns:
        List containing empty results as default implementation.
    """
    # TODO:
    # pass execution to plans
    return [[]]


def declarative_operator_refiner(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Default refiner for declarative operator, returning plans declaratively specified as operator properties.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records to process.
        attributes: Dictionary containing operator-specific parameters.
        properties: Optional properties dictionary containing plan definitions. Defaults to None.

    Returns:
        List containing pipeline definitions based on declarative plans.
    """
    plans = properties['plans']

    if plans is None:
        return []

    # process plan specifications to full pipelines
    pipelines = []

    for plan in plans:
        nodes = plan['nodes']
        mappings = {}
        pipeline = DataPipeline(properties=properties)

        plan_input_node = None
        plan_output_node = None
        # first pass, create nodes/entities
        for node_label in nodes:
            node = nodes[node_label]
            node_type = node['type']
            node_id = None
            if node_type == "OPERATOR":
                operator_name = node['name']
                operator_attributes = node['attributes'] if 'attributes' in node else {}
                operator_properties = node['properties'] if 'properties' in node else {}
                operator_node = pipeline.define_operator(operator_name, attributes=operator_attributes, properties=operator_properties)
                node_id = operator_node.get_id()
            elif node_type == "INPUT":
                input_label = node_label
                input_value = node['value'] if 'value' in node else None
                input_properties = node['properties'] if 'properties' in node else {}
                input_node = pipeline.define_input(label=input_label, value=input_value, properties=input_properties)
                node_id = input_node.get_id()
                # if no value specified, designate as plan input node
                if input_value is None:
                    plan_input_node = input_node
                    plan_input_node.set_data("value", input_data)
                else:
                    input_node.set_data("status", str(Status.EXECUTED))
            elif node_type == "OUTPUT":
                output_label = node_label
                output_value = node['value'] if 'value' in node else None
                output_properties = node['properties'] if 'properties' in node else {}
                output_node = pipeline.define_output(label=output_label, value=output_value, properties=output_properties)
                node_id = output_node.get_id()
                # any output is plan output
                plan_output_node = output_node
            # mappings
            mappings[node_label] = node_id
            mappings[node_id] = node_label

        # create plan input and output nodes, if missing
        if plan_input_node is None:
            plan_input_node = pipeline.define_input(value=input_data, properties={})

        if plan_output_node is None:
            plan_output_node = pipeline.define_output(properties={})
        # second pass, connect
        for node_label in nodes:
            node = nodes[node_label]
            node_id = mappings[node_label]
            # prev
            node_prev = node['prev'] if 'prev' in node else []
            for prev_label in node_prev:
                to_id = node_id
                prev_id = mappings[prev_label]
                pipeline.connect_nodes(from_id, to_id)
            # next
            node_next = node['next'] if 'next' in node else []
            for next_label in node_next:
                from_id = node_id
                to_id = mappings[next_label]
                pipeline.connect_nodes(from_id, to_id)

        # third pass, operators with no prev, connect to input; no next, connect to output
        operators = pipeline.filter_nodes(filter_node_type=["OPERATOR"])
        for operator_id in operators:
            prev_nodes = pipeline.get_prev_nodes(operator_id)
            next_nodes = pipeline.get_next_nodes(operator_id)
            operator_node = pipeline.get_node(operator_id)
            if len(prev_nodes) == 0:
                # connect to input
                pipeline.connect_nodes(plan_input_node, operator_node)
            if len(next_nodes) == 0:
                # connect to output
                pipeline.connect_nodes(operator_node, plan_output_node)

        # set plan input / output
        pipeline.set_plan_input(plan_input_node)
        pipeline.set_plan_output(plan_output_node)

        # add to pipelines
        pipelines.append(pipeline.to_dict())

    return pipelines


def declarative_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate declarative operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    return default_operator_validator(input_data, attributes=attributes, properties=properties)


def declarative_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for declarative operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the declarative operation.
    """
    declarative_operator_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"Declarative operator passed input data to plans specified",
    }
    return declarative_operator_explanation


class DeclarativeOperator(Operator):
    """DeclarativeOperator is a specialized Operator that declaratively specifies the execution of the operator as a set of plans.
    Declarative plans are specified as part of the operator attributes `plans` which are added to the main plan as part of the planning / refine phase.

    Parameters:
        properties: Properties dictionary containing plan definitions and other operator properties. Defaults to None.
    """

    PROPERTIES = {"plans": []}

    name = "declarative_operator"
    description = "Declaratively specifies the execution of the operator as a set of plans"
    default_attributes = {}

    def __init__(self, properties: Dict[str, Any] = None):
        super().__init__(
            properties['name'] if 'name' in properties else self.name,
            function=declarative_operator_function,
            description=properties['description'] if 'description' in properties else self.description,
            properties=properties,
            validator=declarative_operator_validator,
            explainer=declarative_operator_explainer,
            refiner=declarative_operator_refiner,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # refine
        self.properties["refine"] = True
