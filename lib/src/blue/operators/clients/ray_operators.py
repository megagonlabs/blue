###### Blue
from blue.operators.operator import Operator

###### Server specific libs
import ray

###############
### Ray Operators Registry

operators_dict = {}

### Join Operator
try:
    from blue.operators.join_operator import join_operator_function
    
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