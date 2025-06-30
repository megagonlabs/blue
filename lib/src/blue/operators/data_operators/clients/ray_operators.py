###### Blue
from blue.operators.operator import Operator

###### Server specific libs
import ray

###############
### Ray Data Operators Registry
#
# This module provides a centralized registry of all available Ray data operators.
# Each operator is instantiated with @ray.remote decorator and stored in the operators_dict
# for easy access by the RayDataOperatorClient.

operators_dict = {}

### Select Operator
try:
    from blue.operators.data_operators.select_operator import select_operator_function
    
    @ray.remote
    def ray_select_operator(**kwargs):
        return select_operator_function(**kwargs)
    
    select_operator = Operator(
        name=select_operator_function.name,
        description=f"{select_operator_function.description} (Ray distributed)",
        properties={},
        parameters=select_operator_function.parameters,
        validator=select_operator_function.validator,
        explainer=select_operator_function.explainer
    )
    # Override the function with the Ray remote function
    select_operator.function = ray_select_operator
    operators_dict["select"] = select_operator
    print(f"Loaded select operator: {select_operator.name}")
except ImportError as e:
    print(f"Failed to load select operator: {e}")
except Exception as e:
    print(f"Error initializing select operator: {e}")

### Filter Operator
try:
    from blue.operators.data_operators.filter_operator import filter_operator_function
    
    @ray.remote
    def ray_filter_operator(**kwargs):
        return filter_operator_function(**kwargs)
    
    filter_operator = Operator(
        name=filter_operator_function.name,
        description=f"{filter_operator_function.description} (Ray distributed)",
        properties={},
        parameters=filter_operator_function.parameters,
        validator=filter_operator_function.validator,
        explainer=filter_operator_function.explainer
    )
    # Override the function with the Ray remote function
    filter_operator.function = ray_filter_operator
    operators_dict["filter"] = filter_operator
    print(f"Loaded filter operator: {filter_operator.name}")
except ImportError as e:
    print(f"Failed to load filter operator: {e}")
except Exception as e:
    print(f"Error initializing filter operator: {e}")

### Join Operator
try:
    from blue.operators.data_operators.join_operator import join_operator_function
    
    @ray.remote
    def ray_join_operator(**kwargs):
        return join_operator_function(**kwargs)
    
    join_operator = Operator(
        name=join_operator_function.name,
        description=f"{join_operator_function.description} (Ray distributed)",
        properties={},
        parameters=join_operator_function.parameters,
        validator=join_operator_function.validator,
        explainer=join_operator_function.explainer
    )
    # Override the function with the Ray remote function
    join_operator.function = ray_join_operator
    operators_dict["join"] = join_operator
    print(f"Loaded join operator: {join_operator.name}")
except ImportError as e:
    print(f"Failed to load join operator: {e}")
except Exception as e:
    print(f"Error initializing join operator: {e}")

# Print summary of loaded operators
print(f"Loaded {len(operators_dict)} data operators: {list(operators_dict.keys())}") 