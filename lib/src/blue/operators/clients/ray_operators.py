#### utils, types
from typing import List

###### Blue
from blue.operators.operator import Operator
from blue.utils import tool_utils


###############
### Ray Operators Registry
operators_dict = {}

### operator implementations
from blue.operators.join_operator import JoinOperator
from blue.operators.nl2llm_operator import NL2LLMOperator
from blue.operators.nl2sql_operator import NL2SQLOperator

join_operator = JoinOperator()
operators_dict[join_operator.name] = join_operator

nl2llm_operator = NL2LLMOperator()
operators_dict[nl2llm_operator.name] = nl2llm_operator

nl2sql_operator = NL2SQLOperator()
operators_dict[nl2sql_operator.name] = nl2sql_operator
