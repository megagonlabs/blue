###### Blue
from blue.tools.tool import Tool

###### Server specific libs
import ray

tools_dict = {}

### multiply
@ray.remote
def add(numbers=None):
    result = 0
    for number in numbers:
        result += number
    return result

add_tool = Tool(
    name = "add",
    description = "adds numbers and returns the addition as a result",
    properties = {},
    function = add,
    parameters = {
        "numbers": { "type": "list[Union[int, str]", "required": True}           
    },
    validator = lambda params: 'numbers' in params and type(params['numbers']) == list and all([type(number) in [int, float] for number in params['numbers']]),
    explainer = lambda output, params:  { "output": output, "params": params}
)
tools_dict["add"] = add_tool

### multiply
@ray.remote
def multiply(numbers=None):
    result = 1
    for number in numbers:
        result *= number
    return result

multiply_tool = Tool(
    name = "multiply",
    description = "multiplies numbers and returns the multiplication ion as a result",
    properties = {},
    function = multiply,
    parameters = {
        "numbers": { "type": "list[Union[int, str]", "required": True}           
    },
    validator = lambda params: 'numbers' in params and type(params['numbers']) == list and all([type(number) in [int, float] for number in params['numbers']]),
    explainer = lambda output, params: { "output": output, "params": params}
)
tools_dict["multiply"] = multiply_tool

