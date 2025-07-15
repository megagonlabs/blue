#### utils, types
from typing import List

###### Blue
from blue.operators.operator import Operator
from blue.utils import tool_utils


###############
### Ray Operators Registry
operators_dict = tools_dict = {}

### operator implementations
from blue.operators.join_operator import join_operator_function, join_operator_validator, join_operator_explainer
from blue.operators.nl2llm_operator import nl2llm_operator_function, nl2llm_operator_validator, nl2llm_operator_explainer
from blue.operators.nl2sql_operator import nl2sql_operator_function, nl2sql_operator_validator, nl2sql_operator_explainer

join_operator = Operator(
    name=join_operator_function.name,
    description=f"{join_operator_function.description} (Ray)",
    properties={},
    function=join_operator_function,
    parameters=tool_utils.extract_signature(join_operator_function, mcp_format=True)['parameters'],
    validator=join_operator_validator,
    explainer=join_operator_explainer,
)

nl2sql_operator = Operator(
    name=nl2sql_operator_function.name,
    description=f"{nl2sql_operator_function.description} (Ray)",
    properties={},
    function=nl2sql_operator_function,
    parameters=tool_utils.extract_signature(nl2sql_operator_function, mcp_format=True)['parameters'],
    validator=nl2sql_operator_validator,
    explainer=nl2sql_operator_explainer,
)

nl2llm_operator = Operator(
    name=nl2llm_operator_function.name,
    description=f"{nl2llm_operator_function.description} (Ray)",
    properties={},
    function=nl2llm_operator_function,
    parameters=tool_utils.extract_signature(nl2llm_operator_function, mcp_format=True)['parameters'],
    validator=nl2llm_operator_validator,
    explainer=nl2llm_operator_explainer,
)
