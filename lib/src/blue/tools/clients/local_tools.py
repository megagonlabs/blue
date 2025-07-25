#### utils, types
from typing import List

###### Blue
from blue.tools.tool import Tool

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
    "add",
    add,
    description="adds numbers and returns the addition as a result",
    validator=lambda params: 'numbers' in params and type(params['numbers']) == list and all([type(number) in [int, float] for number in params['numbers']]),
    explainer=lambda output, params: {"output": output, "params": params},
)
tools_dict["add"] = add_tool


### multiply
def multiply(numbers: List[int], x: int = 1) -> int:
    result = 1
    for number in numbers:
        result *= number * x
    return result


multiply_tool = Tool(
    "multiply",
    multiply,
    description="multiplies numbers and returns the multiplication ion as a result",
    validator=lambda params: 'numbers' in params and type(params['numbers']) == list and all([type(number) in [int, float] for number in params['numbers']]),
    explainer=lambda output, params: {"output": output, "params": params},
)
# example to hide a parameter
multiply_tool.properties['signature']['parameters']['x']['hidden'] = True
tools_dict["multiply"] = multiply_tool
