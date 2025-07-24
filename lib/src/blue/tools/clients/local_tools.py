#### utils, types
from typing import List

###### Blue
from blue.tools.tool import Tool
from blue.utils import tool_utils

###############
### Local Tools Registry
tools_dict = {}


### add
def add(numbers: List[int]) -> int:
    result = 0
    for number in numbers:
        result += number
    return result


add_tool = Tool(
    name="add",
    description="adds numbers and returns the addition as a result",
    properties={},
    function=add,
    signature=tool_utils.extract_signature(add, mcp_format=True),
    validator=lambda params: 'numbers' in params and type(params['numbers']) == list and all([type(number) in [int, float] for number in params['numbers']]),
    explainer=lambda output, params: {"output": output, "params": params},
)
tools_dict["add"] = add_tool


### multiply
def multiply(numbers: List[int]) -> int:
    result = 1
    for number in numbers:
        result *= number
    return result


multiply_tool = Tool(
    name="multiply",
    description="multiplies numbers and returns the multiplication ion as a result",
    properties={},
    function=multiply,
    signature=tool_utils.extract_signature(multiply, mcp_format=True),
    validator=lambda params: 'numbers' in params and type(params['numbers']) == list and all([type(number) in [int, float] for number in params['numbers']]),
    explainer=lambda output, params: {"output": output, "params": params},
)
tools_dict["multiply"] = multiply_tool
