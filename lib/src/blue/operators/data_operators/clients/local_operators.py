###### Blue
from blue.operators.operator import Operator

###############
### Local Data Operators Registry
#
# This module provides a centralized registry of all available local data operators.
# Each operator is instantiated and stored in the operators_dict for easy access
# by the LocalDataOperatorClient.

operators_dict = {}

### Select Operator
try:
    from blue.operators.data_operators.select_operator import select_operator_function
    
    select_operator = Operator(
        name=select_operator_function.name,
        description=select_operator_function.description,
        properties={},
        parameters=select_operator_function.parameters,
        function=select_operator_function,
        validator=select_operator_function.validator,
        explainer=select_operator_function.explainer
    )
    operators_dict["select"] = select_operator
    print(f"Loaded select operator: {select_operator.name}")
except ImportError as e:
    print(f"Failed to load select operator: {e}")
except Exception as e:
    print(f"Error initializing select operator: {e}")

### Filter Operator
try:
    from blue.operators.data_operators.filter_operator import filter_operator_function
    
    filter_operator = Operator(
        name=filter_operator_function.name,
        description=filter_operator_function.description,
        properties={},
        parameters=filter_operator_function.parameters,
        function=filter_operator_function,
        validator=filter_operator_function.validator,
        explainer=filter_operator_function.explainer
    )
    operators_dict["filter"] = filter_operator
    print(f"Loaded filter operator: {filter_operator.name}")
except ImportError as e:
    print(f"Failed to load filter operator: {e}")
except Exception as e:
    print(f"Error initializing filter operator: {e}")

### Join Operator
try:
    from blue.operators.data_operators.join_operator import join_operator_function
    
    join_operator = Operator(
        name=join_operator_function.name,
        description=join_operator_function.description,
        properties={},
        parameters=join_operator_function.parameters,
        function=join_operator_function,
        validator=join_operator_function.validator,
        explainer=join_operator_function.explainer
    )
    operators_dict["join"] = join_operator
    print(f"Loaded join operator: {join_operator.name}")
except ImportError as e:
    print(f"Failed to load join operator: {e}")
except Exception as e:
    print(f"Error initializing join operator: {e}")

# Print summary of loaded operators
print(f"Loaded {len(operators_dict)} data operators: {list(operators_dict.keys())}")

###############
### Utility Functions

def get_available_operators():
    """Get list of available operator names."""
    return list(operators_dict.keys())

def get_operator(operator_name: str):
    """Get a specific operator by name."""
    return operators_dict.get(operator_name)

def get_operators_info():
    """Get information about all available operators."""
    info = {}
    for name, operator in operators_dict.items():
        info[name] = {
            "name": operator.name,
            "description": operator.description,
            "parameters": operator.parameters,
            "tool_type": operator.properties.get("tool_type", "unknown")
        }
    return info

def validate_operator_exists(operator_name: str) -> bool:
    """Check if an operator exists."""
    return operator_name in operators_dict 