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
from blue.operators.data_discover_operator import DataDiscoverOperator
from blue.operators.select_operator import SelectOperator
from blue.operators.project_operator import ProjectOperator
from blue.operators.insert_operator import InsertOperator
from blue.operators.delete_operator import DeleteOperator

join_operator = JoinOperator()
operators_dict[join_operator.name] = join_operator

nl2llm_operator = NL2LLMOperator()
operators_dict[nl2llm_operator.name] = nl2llm_operator

nl2sql_operator = NL2SQLOperator()
operators_dict[nl2sql_operator.name] = nl2sql_operator

data_discover_operator = DataDiscoverOperator()
operators_dict[data_discover_operator.name] = data_discover_operator

select_operator = SelectOperator()
operators_dict[select_operator.name] = select_operator

project_operator = ProjectOperator()
operators_dict[project_operator.name] = project_operator

insert_operator = InsertOperator()
operators_dict[insert_operator.name] = insert_operator

delete_operator = DeleteOperator()
operators_dict[delete_operator.name] = delete_operator
