###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy
import logging
from typing import List, Dict, Any, Callable, Union, Optional
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError

###### Blue
from blue.tools.tool import Tool
from blue.utils import json_utils
from blue.utils.py_type_utils import string_to_python_type, create_pydantic_model, validate_parameter_type

###############
### Operator

class Operator(Tool):
    """
    Operator is a specialized Tool to perform data operations in Blue (JSON array data records).
    Inputs: always expects multiple data inputs as a list of data sources: [data_1, data_2, ...], where each data source is a JSON array of records, which represents a data source/group.
    Outputs: always returns a JSON array of records.
    Operator doesn't listen to any data stream, it only processes data when called.
    
    Key differences from Tool:
    - Always expects input_data parameter (list of data sources)
    - Always returns JSON array of records
    - Has operator-specific properties and validation
    - Can be identified by servers as an operator type
    """

    def __init__(self, name: str, description: str, properties: Dict[str, Any] = None, parameters: Dict[str, Any] = None, function: Callable = None, validator: Callable = None, explainer: Callable = None):
        """
        Initialize an Operator.
        
        Args:
            name: Name of the operator
            description: Description of what the operator does
            properties: Additional properties for the operator
            parameters: Parameter definitions for the operator
            function: Custom function to execute (uses _execute_operator if None)
            validator: Function to validate input parameters
            explainer: Function to explain output and potential errors
        """
        self.name = name
        self.description = description
        self.properties = properties
        self.parameters = parameters
        self.validator = validator
        self.explainer = explainer
        
        # Initialize properties, parameters, validator, and explainer
        if properties is None:
            self.properties = {}
        if parameters is None:
            self.parameters = {}
        if validator is None:
            self.validator = self._default_validator
        if explainer is None:
            self.explainer = self._default_explainer
        
        # Initialize properties first
        self._initialize(properties=properties)
            
        # Set default parameters for operators
        default_parameters = {
            "input_data": {
                "type": "list[list[dict]]",
                "description": "List of data groups, each containing JSON array of records",
                "required": True
            }
        }
        
        # Merge with provided parameters
        merged_parameters = copy.deepcopy(default_parameters)
        if parameters:
            merged_parameters.update(parameters)
        
        # Add operator-specific properties
        operator_properties = copy.deepcopy(self.properties)
        operator_properties["tool_type"] = "operator"
        operator_properties["category"] = "data_processing"
        
        # Use provided function or default to _execute_operator
        operator_function = function if function is not None else self._execute_operator
        
        super().__init__(
            name=name,
            description=description,
            properties=operator_properties,
            function=operator_function,
            parameters=merged_parameters,
            validator=validator,
            explainer=explainer
        )

        # Ensure function, validator, and explainer are set to defaults if not provided
        if not hasattr(self, 'function') or self.function is None:
            self.function = self._execute_operator
        if not hasattr(self, 'validator') or self.validator is None:
            self.validator = self._default_validator
        if not hasattr(self, 'explainer') or self.explainer is None:
            self.explainer = self._default_explainer
    
    def _initialize(self, properties=None):
        """Initialize the Operator following the same pattern as Agent."""
        self._initialize_properties()
        self._update_properties(properties=properties)
    
    def _initialize_properties(self):
        """Initialize default properties for operators."""
        self.properties = {}
        
        # Operator identification properties
        self.properties["tool_type"] = "operator"

        # Data validation properties
        self.properties["validate_input"] = True
        self.properties["validate_output"] = True
        self.properties["validation_error_handling"] = "fail"  # fail, log, skip
        
        # Processing properties
        self.properties["max_records"] = None  # None means no limit
        self.properties["timeout"] = 300  # 5 minutes timeout
        
        # Error handling properties
        self.properties["error_handling"] = "skip"  # fail, log, skip
        self.properties["log_processing_stats"] = True
    
    def _update_properties(self, properties=None):
        """Update properties following the same pattern as Agent._update_properties()."""
        if properties is None:
            return

        # Override existing properties
        for p in properties:
            self.properties[p] = properties[p]
    
    def get_properties(self, properties=None):
        """Get merged properties, following the same pattern as RequestorOperator.get_properties()."""
        merged_properties = {}

        # Copy operator properties
        for p in self.properties:
            merged_properties[p] = self.properties[p]

        # Override with provided properties
        if properties is not None:
            for p in properties:
                merged_properties[p] = properties[p]

        return merged_properties
    
    @classmethod
    def validate_parameters(cls, params: Dict[str, Any], parameters: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
        """Standalone parameter validation that can be called without creating an instance."""
        if properties is None:
            properties = {}
        
        validate_input = properties.get("validate_input", True)
        validation_error_handling = properties.get("validation_error_handling", "fail")
        
        if not validate_input:
            return True  # Skip validation if disabled
        
        # Validate required parameters
        for param_name, param_def in parameters.items():
            required = param_def.get("required", False)
            
            # Check if required parameter is present
            if required and param_name not in params:
                return False
            
            # If parameter is present, validate its type
            if param_name in params:
                param_value = params[param_name]
                param_type = param_def.get("type")
                
                if param_type:
                    try:
                        if not validate_parameter_type(param_value, param_type):
                            return False
                    except RuntimeError as e:
                        # System failure in validation - handle based on configuration
                        error_msg = f"Parameter validation system error for '{param_name}': {e}"
                        
                        if validation_error_handling == "fail":
                            logging.error(error_msg)
                            return False
                        elif validation_error_handling == "log":
                            logging.warning(error_msg)
                            return False
                        else:  # skip
                            logging.info(error_msg)
                            # Continue with validation (treat as if validation passed)
                    except Exception as e:
                        # Other system failures should propagate to error handling
                        raise e
        
        # Validate input_data specifically (always required for operators)
        if 'input_data' not in params:
            return False
            
        input_data = params['input_data']
        if not isinstance(input_data, list):
            return False
            
        # Check if all data sources are lists of lists of dictionaries
        for i, data in enumerate(input_data):
            if not isinstance(data, list):
                return False
            for item in data:
                if not isinstance(item, dict):
                    return False
                
        return True

    def _default_validator(self, params: Dict[str, Any]) -> bool:
        """Default validator for operator parameters."""
        return self.validate_parameters(params, self.parameters, self.properties)
    
    def _default_explainer(self, output: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Default explainer for operator output."""
        input_data = params.get('input_data', [])
        input_counts = {f"source_{i}": len(data) for i, data in enumerate(input_data)}
        total_input_records = sum(input_counts.values())
        
        output_count = len(output) if isinstance(output, list) else 1
        
        explanation = {
            "output": output,
            "params": params,
            "statistics": {
                "input_records": total_input_records,
                "input_sources": input_counts,
                "output_records": output_count,
                "transformation_ratio": output_count / total_input_records if total_input_records > 0 else 0
            }
        }
        return explanation

    def _execute_operator(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Main entry point for operator execution.
        This method orchestrates the complete execution flow.
        
        Args:
            **kwargs: Parameters including 'input_data' and operator-specific parameters
            
        Returns:
            Processed data as a list of dictionaries
        """
        try:
            # Step 1: Validate parameters
            if not self.validator(kwargs):
                raise ValueError("Parameter validation failed")
            
            # Step 2: Extract input data
            input_data = kwargs.get('input_data', [])
            if not input_data:
                return []
            
            # Step 3: Preprocess input data
            processed_input = self._process_input_data(input_data, kwargs)
            
            # Step 4: Execute operator-specific logic
            result = self._execute_operator_logic(processed_input, kwargs)
            
            # Step 5: Postprocess result (if needed)
            final_result = self._process_output_data(result, kwargs)
            
            return final_result
            
        except Exception as e:
            # Get properties for error handling
            properties = self.get_properties()
            error_handling = properties.get("error_handling", "skip")
            
            if error_handling == "fail":
                raise e
            elif error_handling == "log":
                logging.error(f"Error in {self.name}, skipping: {str(e)}")
                return []
            else:  # skip
                logging.warning(f"Error in {self.name}, skipping: {str(e)}")
                return []
    
    def _process_input_data(self, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """
        Preprocess input data after validation and before operator logic execution.
        This method handles data preparation, transformation, and validation.
        
        Args:
            input_data: List of data sources, each containing JSON array of records
            params: Parameters for the operation
            
        Returns:
            Preprocessed input data
        """
        # Default implementation: return input data as-is
        # Subclasses can override this for specific preprocessing needs
        return input_data
    
    def _execute_operator_logic(self, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute the actual operator-specific logic.
        This method contains the core business logic for each operator type.
        """
        # Default implementation: return first data source
        # Subclasses MUST override this with their specific logic
        if input_data and len(input_data) > 0:
            return input_data[0]
        return []
    
    def _process_output_data(self, result: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Postprocess the result after operator logic execution.
        This method handles result formatting, validation, and final transformations.
        
        Args:
            result: Result from operator logic
            params: Parameters for the operation
            
        Returns:
            Final processed result
        """
        # Default implementation: return result as-is
        # Subclasses can override this for specific postprocessing needs
        return result

    def get_data_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the input data."""
        if not data:
            return {
                "record_count": 0,
                "fields": [],
                "field_types": {}
            }
        
        # Get all unique field names
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        # Analyze field types
        field_types = {}
        for field in all_fields:
            types = set()
            for record in data:
                if field in record:
                    types.add(type(record[field]).__name__)
            field_types[field] = list(types)
        
        return {
            "record_count": len(data),
            "fields": list(all_fields),
            "field_types": field_types
        }
    
    def get_data_sources_statistics(self, input_data: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Get statistics about all data sources."""
        statistics = {
            "total_sources": len(input_data),
            "sources": {}
        }
        
        for i, data in enumerate(input_data):
            statistics["sources"][f"source_{i}"] = self.get_data_statistics(data)
        
        # Calculate totals
        total_records = sum(stats["record_count"] for stats in statistics["sources"].values())
        statistics["total_records"] = total_records
        
        return statistics
    
    def filter_records(self, data: List[Dict[str, Any]], condition: Callable) -> List[Dict[str, Any]]:
        """Filter records based on a condition function."""
        return [record for record in data if condition(record)]
    
    def transform_records(self, data: List[Dict[str, Any]], transform: Callable) -> List[Dict[str, Any]]:
        """Transform records using a transform function."""
        return [transform(record) for record in data]
    
    def aggregate_records(self, data: List[Dict[str, Any]], group_by: str, aggregate_func: Callable, value_field: str) -> List[Dict[str, Any]]:
        """Aggregate records by grouping and applying an aggregation function."""
        groups = {}
        
        for record in data:
            if group_by in record and value_field in record:
                group_key = record[group_by]
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(record[value_field])
        
        result = []
        for group_key, values in groups.items():
            result.append({
                group_by: group_key,
                f"{value_field}_{aggregate_func.__name__}": aggregate_func(values)
            })
        
        return result

    @classmethod
    def is_operator(cls, tool_or_operator) -> bool:
        """
        Check if a tool/operator is actually an operator.
        
        Args:
            tool_or_operator: Tool or Operator object to check
            
        Returns:
            True if it's an operator, False otherwise
        """
        if hasattr(tool_or_operator, 'properties'):
            return tool_or_operator.properties.get("tool_type") == "operator"
        return False

    @classmethod
    def get_operator_type(cls, tool_or_operator) -> str:
        """
        Get the type of a tool/operator.
        
        Args:
            tool_or_operator: Tool or Operator object to check
            
        Returns:
            "operator" if it's an operator, "tool" otherwise
        """
        if cls.is_operator(tool_or_operator):
            return "operator"
        return "tool" 