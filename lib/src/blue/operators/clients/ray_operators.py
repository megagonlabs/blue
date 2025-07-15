#### utils, types
from typing import List

###### Blue
from blue.operators.operator import Operator
from blue.utils import tool_utils


###############
### Ray Operators Registry
operators_dict = tools_dict = {}

### join
from blue.operators.join_operator import join_operator_function, join_operator_validator, join_operator_explainer


join_operator = Operator(
    name=join_operator_function.name,
    description=f"{join_operator_function.description} (Ray)",
    properties={},
    function=join_operator_function,
    parameters=tool_utils.extract_signature(join_operator_function, mcp_format=True)['parameters'],
    validator=join_operator_validator,
    explainer=join_operator_explainer,
)
