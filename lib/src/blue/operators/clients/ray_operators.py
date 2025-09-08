#### utils, types
from typing import List

###### Blue
from blue.operators.operator import Operator, DeclarativeOperator
from blue.utils import tool_utils


###############
### Ray Operators Registry
operators_dict = {}

##### operator implementations
## PLAN OPERATORS
from blue.operators.operator_discover import OperatorDiscoverOperator

operator_discover_operator = OperatorDiscoverOperator()
operators_dict[operator_discover_operator.name] = operator_discover_operator

from blue.operators.plan_discover import PlanDiscoverOperator

plan_discover_operator = PlanDiscoverOperator()
operators_dict[plan_discover_operator.name] = plan_discover_operator

## META OPERATORS
from blue.operators.data_discover_operator import DataDiscoverOperator

data_discover_operator = DataDiscoverOperator()
operators_dict[data_discover_operator.name] = data_discover_operator

from blue.operators.query_breakdown_operator import QueryBreakdownOperator

query_breakdown_operator = QueryBreakdownOperator()
operators_dict[query_breakdown_operator.name] = query_breakdown_operator

question_answer_operator = DeclarativeOperator(properties={"name": "question_answer", "description": "answer questions", "plans": [{}]})
operators_dict[question_answer_operator.name] = question_answer_operator

## RELATIONAL OPERATORS
from blue.operators.select_operator import SelectOperator

select_operator = SelectOperator()
operators_dict[select_operator.name] = select_operator

from blue.operators.project_operator import ProjectOperator

project_operator = ProjectOperator()
operators_dict[project_operator.name] = project_operator

from blue.operators.join_operator import JoinOperator

join_operator = JoinOperator()
operators_dict[join_operator.name] = join_operator

from blue.operators.insert_operator import InsertOperator

insert_operator = InsertOperator()
operators_dict[insert_operator.name] = insert_operator

from blue.operators.delete_operator import DeleteOperator

delete_operator = DeleteOperator()
operators_dict[delete_operator.name] = delete_operator

from blue.operators.create_database_operator import CreateDatabaseOperator

create_database_operator = CreateDatabaseOperator()
operators_dict[create_database_operator.name] = create_database_operator

## EXTENDED RELATIONAL OPERATORS

## DATA TRANSFORMATION OPERATORS

## SET OPERATORS
from blue.operators.union_operator import UnionOperator

union_operator = UnionOperator()
operators_dict[union_operator.name] = union_operator

from blue.operators.intersect_operator import IntersectOperator

intersect_operator = IntersectOperator()
operators_dict[intersect_operator.name] = intersect_operator

## LOGICAL OPERATORS

## TEXT OPERATORS

## SEMANTIC OPERATORS

## QUERY/COMPOUND OPERATORS
from blue.operators.nl2llm_operator import NL2LLMOperator

nl2llm_operator = NL2LLMOperator()
operators_dict[nl2llm_operator.name] = nl2llm_operator

from blue.operators.nl2sql_operator import NL2SQLOperator

nl2sql_operator = NL2SQLOperator()
operators_dict[nl2sql_operator.name] = nl2sql_operator

## REVERSE QUERY OPERATORS

## VECTOR OPERATORS

## ARITHMETIC OPERATORS

## CUSTOM OPERATORS
