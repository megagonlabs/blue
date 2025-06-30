###### Parsers, Formats, Utils
import logging
from typing import List, Dict, Any, Optional, Union

###### Blue
from blue.operators.operator import Operator

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

###############
### Join Operator Core Function

def _join_operator_core(**kwargs):
    """
    Core join operator function that joins two JSON array data sources,
    following pandas DataFrame join design.
    
    Args:
        input_data: List of exactly 2 data sources, each containing JSON array of records
        left_on: Field name(s) from left data source to join on (str or list of str)
        right_on: Field name(s) from right data source to join on (str or list of str)
        how: Type of join: 'inner', 'left', 'right', 'outer'
        left_suffix: Suffix to add to left data source field names to avoid conflicts
        right_suffix: Suffix to add to right data source field names to avoid conflicts
        
    Returns:
        Joined JSON array
    """
    # Extract parameters
    input_data = kwargs.get('input_data', [])
    left_on = kwargs.get('left_on', [])
    right_on = kwargs.get('right_on', [])
    how = kwargs.get('how', 'inner')
    left_suffix = kwargs.get('left_suffix', '_left')
    right_suffix = kwargs.get('right_suffix', '_right')
    
    # Validate input
    if not input_data or len(input_data) != 2:
        return []
    
    left_data = input_data[0]
    right_data = input_data[1]
    
    # Convert single field names to lists for consistency
    if isinstance(left_on, str):
        left_on = [left_on]
    if isinstance(right_on, str):
        right_on = [right_on]
    
    # Validate field lists have same length
    if len(left_on) != len(right_on):
        return []
    
    # If no join fields specified, return empty result
    if len(left_on) == 0:
        return []
    
    # Process the join
    return _perform_join(left_data, right_data, left_on, right_on, how, left_suffix, right_suffix)

###############
### Join Operator Function with Metadata

def join_operator_validator(params: Dict[str, Any]) -> bool:
    """Validate join operator parameters with type checking and join-specific logic."""
    # Call the default parameter validation for type/required checks
    from blue.operators.operator import Operator
    
    if not Operator.validate_parameters(params, join_operator_function.parameters):
        return False
    
    # Additional join-specific validation
    input_data = params['input_data']
    if len(input_data) != 2:
        return False
    
    left_on = params['left_on']
    right_on = params['right_on']
    
    # Convert to list if string for consistent processing
    if isinstance(left_on, str):
        left_on = [left_on]
    if isinstance(right_on, str):
        right_on = [right_on]
    
    # Validate join field requirements
    if len(left_on) != len(right_on):
        return False
    if len(left_on) == 0:
        return False
    
    # Validate join type
    how = params.get('how', 'inner')
    supported_join_types = ['inner', 'left', 'right', 'outer']
    if how not in supported_join_types:
        return False
    
    return True

def join_operator_explainer(output: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """Explain join operator results."""
    return {
        "operation": "join",
        "how": params.get('how', 'inner'),
        "left_on": params.get('left_on', []),
        "right_on": params.get('right_on', []),
        "left_suffix": params.get('left_suffix', '_left'),
        "right_suffix": params.get('right_suffix', '_right'),
        "input_records": sum(len(data) for data in params.get('input_data', [])) if params.get('input_data') else 0,
        "output_records": len(output) if isinstance(output, list) else 0,
        "parameters": params
    }

# Create the join operator function with metadata
join_operator_function = _join_operator_core
join_operator_function.name = "join"
join_operator_function.description = "Joins two JSON array data sources, following pandas DataFrame join design"
join_operator_function.parameters = {
    "left_on": {
        "type": "str|list[str]",
        "description": "Field name(s) from left data source to join on",
        "required": True
    },
    "right_on": {
        "type": "str|list[str]",
        "description": "Field name(s) from right data source to join on",
        "required": True
    },
    "how": {
        "type": "str",
        "description": "Type of join: 'inner', 'left', 'right', 'outer'",
        "required": False,
        "default": "inner"
    },
    "left_suffix": {
        "type": "str",
        "description": "Suffix to add to left data source field names to avoid conflicts",
        "required": False,
        "default": "_left"
    },
    "right_suffix": {
        "type": "str",
        "description": "Suffix to add to right data source field names to avoid conflicts",
        "required": False,
        "default": "_right"
    }
}
join_operator_function.validator = join_operator_validator
join_operator_function.explainer = join_operator_explainer

###############
### Helper Functions

def _perform_join(left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
                 left_on: List[str], right_on: List[str], how: str, 
                 left_suffix: str, right_suffix: str) -> List[Dict[str, Any]]:
    """
    Perform the actual join operation.
    
    Args:
        left_data: Left data source
        right_data: Right data source
        left_on: Field names from left data source
        right_on: Field names from right data source
        how: Type of join
        left_suffix: Suffix for left field names
        right_suffix: Suffix for right field names
        
    Returns:
        Joined data
    """
    # Build index for right data
    right_index = {}
    for record in right_data:
        # Create composite key from all join fields
        key_values = []
        for field in right_on:
            if field in record:
                key_values.append(record[field])
            else:
                key_values.append(None)
        key = tuple(key_values)
        
        if key not in right_index:
            right_index[key] = []
        right_index[key].append(record)
    
    # Perform join based on type
    if how == 'inner':
        return _inner_join(left_data, right_data, left_on, right_on, right_index, left_suffix, right_suffix)
    elif how == 'left':
        return _left_join(left_data, right_data, left_on, right_on, right_index, left_suffix, right_suffix)
    elif how == 'right':
        return _right_join(left_data, right_data, left_on, right_on, right_index, left_suffix, right_suffix)
    elif how == 'outer':
        return _outer_join(left_data, right_data, left_on, right_on, right_index, left_suffix, right_suffix)
    else:
        return []

def _get_join_key(record: Dict[str, Any], fields: List[str]) -> tuple:
    """Get composite join key from record."""
    key_values = []
    for field in fields:
        if field in record:
            key_values.append(record[field])
        else:
            key_values.append(None)
    return tuple(key_values)

def _inner_join(left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
               left_on: List[str], right_on: List[str], right_index: Dict[tuple, List[Dict[str, Any]]], 
               left_suffix: str, right_suffix: str) -> List[Dict[str, Any]]:
    """Perform inner join."""
    result = []
    
    for left_record in left_data:
        left_key = _get_join_key(left_record, left_on)
        if left_key in right_index:
            for right_record in right_index[left_key]:
                merged_record = _merge_records(left_record, right_record, left_suffix, right_suffix)
                result.append(merged_record)
    
    return result

def _left_join(left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
              left_on: List[str], right_on: List[str], right_index: Dict[tuple, List[Dict[str, Any]]], 
              left_suffix: str, right_suffix: str) -> List[Dict[str, Any]]:
    """Perform left join."""
    result = []
    
    for left_record in left_data:
        left_key = _get_join_key(left_record, left_on)
        if left_key in right_index:
            for right_record in right_index[left_key]:
                merged_record = _merge_records(left_record, right_record, left_suffix, right_suffix)
                result.append(merged_record)
        else:
            # No match found, include left record with null right fields
            merged_record = _merge_records(left_record, {}, left_suffix, right_suffix)
            result.append(merged_record)
    
    return result

def _right_join(left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
               left_on: List[str], right_on: List[str], right_index: Dict[tuple, List[Dict[str, Any]]], 
               left_suffix: str, right_suffix: str) -> List[Dict[str, Any]]:
    """Perform right join."""
    result = []
    
    # Track matched right records
    matched_right_keys = set()
    
    # First, do inner join
    for left_record in left_data:
        left_key = _get_join_key(left_record, left_on)
        if left_key in right_index:
            matched_right_keys.add(left_key)
            for right_record in right_index[left_key]:
                merged_record = _merge_records(left_record, right_record, left_suffix, right_suffix)
                result.append(merged_record)
    
    # Then add right records that don't have matches
    for right_record in right_data:
        right_key = _get_join_key(right_record, right_on)
        if right_key not in matched_right_keys:
            # No match found, include right record with null left fields
            merged_record = _merge_records({}, right_record, left_suffix, right_suffix)
            result.append(merged_record)
    
    return result

def _outer_join(left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
               left_on: List[str], right_on: List[str], right_index: Dict[tuple, List[Dict[str, Any]]], 
               left_suffix: str, right_suffix: str) -> List[Dict[str, Any]]:
    """Perform outer join."""
    result = []
    
    # Track matched keys
    matched_left_keys = set()
    matched_right_keys = set()
    
    # Do inner join first
    for left_record in left_data:
        left_key = _get_join_key(left_record, left_on)
        if left_key in right_index:
            matched_left_keys.add(left_key)
            matched_right_keys.add(left_key)
            for right_record in right_index[left_key]:
                merged_record = _merge_records(left_record, right_record, left_suffix, right_suffix)
                result.append(merged_record)
    
    # Add unmatched left records
    for left_record in left_data:
        left_key = _get_join_key(left_record, left_on)
        if left_key not in matched_left_keys:
            merged_record = _merge_records(left_record, {}, left_suffix, right_suffix)
            result.append(merged_record)
    
    # Add unmatched right records
    for right_record in right_data:
        right_key = _get_join_key(right_record, right_on)
        if right_key not in matched_right_keys:
            merged_record = _merge_records({}, right_record, left_suffix, right_suffix)
            result.append(merged_record)
    
    return result

def _merge_records(left_record: Dict[str, Any], right_record: Dict[str, Any], 
                  left_suffix: str, right_suffix: str) -> Dict[str, Any]:
    """
    Merge two records with suffix handling.
    
    Args:
        left_record: Record from left data source
        right_record: Record from right data source
        left_suffix: Suffix for left field names
        right_suffix: Suffix for right field names
        
    Returns:
        Merged record
    """
    merged_record = {}
    
    # Add left record fields with suffix
    for field, value in left_record.items():
        field_name = f"{field}{left_suffix}"
        merged_record[field_name] = value
    
    # Add right record fields with suffix
    for field, value in right_record.items():
        field_name = f"{field}{right_suffix}"
        merged_record[field_name] = value
    
    return merged_record
