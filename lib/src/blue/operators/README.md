# Operators

Data Operators are functions that are purely focused on data processing over data in various modalities, including text, structured data, graph data, and beyond. In blue data operators are implemented as special tools (see [Tools](lib/src/blue/tools) that have a specific signature.

Data pipelines can be manually constructed by chaining a number of operators in a specical DAG, called `Pipeline`. They can be used by any agent, such as tool-enabled agents, to process data for example.

Alternatively, operators can be chained by means of a data planner (see [Data Sources and Processing](lib/src/blue/data) for an experimental data planner that utilizes operators and creates and executes a pipeline.

Operators can be abstract (or logical) where one or more physical operators can perform the actual execution of operation. For example, an extract operator can be implemented using BERT, LLM, dictionary approaches, etc. These different operators can be organized in a hierarchy, where actual operator selection can be performed later by an optimizer. Abstract operators essentially refine the task into a set of plans, comprised of operators.

In blue we are still actively expanding the set of operators but we have several classes of operators:
* Plan Operators: Operators that are used in planning and beyond, e.g. `PlanDiscoverOperator`, to create high-level plans, `OperatorDiscoverOperator` to help search operators from operator registry, `DataDiscoverOperator` to help search data from data regitry, `QueryBreakdownOperator` to breakdown query into subqueries.
* Relational Operators: Operators typical in relational algebra, e.g. `SelectOperator`, `ProjectOperator`, `JoinOperator`, `InsertOperator`, `DeleteOperator`.
* Source Operators: Operators that perform data management tasks such as `CreateDatabaseOperator`, `CreateTableOperator`.
* Query/Compound Operators: Operators that can execute queries against various data sources, e.g. `NL2SQLOperator`, to query SQL databases, `NL2LLMOperator` to query LLMs data, as well as `NL2QueryRouterOperator` to route a query based on source type, and `MultipartQueryOperator` to orchestrate the execution of multi-part query, starting with data discovery.
* Semantic Operators: Operators that use LLMs to perform operations such as `SemanticExtractOperator`, `SemanticFilterOperator`, `SemanticProjectOperator`, and `SemanticTransformOperator`, to extract, filter, project and transform textual data to produce structured data.
* Set Operators: Operators that do set operations, such as `IntersectOperator` and `UnionOperator`.

Expect the set of operators to grow in the near future!

## Operator Development

`Operator` class is an extension of `Tool`. Just like tools, operators too define `function` to execute operation, `validator` to validate input data, and `explainer` to explain results. In addition, operators also (optionally) define `refiner` to refine task into a set of plans (used mainly by abstract operators). 

`Operator` functions have a special signature, as described below:

```
function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
```

### Operator Input and Output Data

One key characteristics is that input data and output data from functions is the same type, `List[List[Dict[str, Any]]]`. This allows outputs from operators to be passed onto next operator to be processed, e.g. chaining operators. In terms of the data it represents it is pretty flexible. In relational sense, it can be considered as a list of tables, where a table itself is a list of records, e.g. a dictionary of key-value pairs. 

For example:
```
[[
   {"job_title": "operations manager", "company_name": "FOOD COLLECTIVE PTE. LTD.", "location": ""}, 
   {"job_title": "project manager", "company_name": "VISION DISPLAY PTE. LTD.", "location": "geylang"}, 
   {"job_title": "market development manager (asean)", "company_name": "HAULIO PTE. LTD.", "location": ""}, 
   {"job_title": "consultant, applications", "company_name": "INFOSYS COMPAZ PTE. LTD.", "location": ""}, 
   {"job_title": "assistant director, office of data governance", "company_name": "SINGAPORE HEALTH SERVICES PTE LTD", "location": ""}
]]
```

### Opeartor Attributes

Operator attributes are essentially a dictionary of key-value pairs that govern the execution of a instance of operation. For example, for `JoinOperator` it would contain keys to join on (e.g. `join_on`). 

Each operator defines not only the list of attributes, but also its metadata, such as:
```
{
  "join_on": {
    "type": "list[list[str]]",
    "description": "List of join key lists for each data source",
    "required": true
  },
  "join_type": {
    "type": "str",
    "description": "Type of join: 'inner', 'left', 'right', 'outer'",
    "required": false,
    "default": "inner"
  },
  ...
}
```

Attributes are set at the time of execution either manually when designing the pipeline or by the data planner automatically.

### Operator Properties

Like attributes, operator properties are also a dictionary of key-value pairs that govern the execution of a instance of operation but more so on a macro level. For example, for a `SemanticExtractOperator` it would contain a property such as `openai.model`. 

Properties are defined in the registry but can be overriden by the planner, particular by an optimizer to select a cheaper model to reduce costs.

## Operator Servers

Similar tool servers, there are also three types of operators servers, each come with different pros and cons for different use cases: Local operators that execute locally; Ray based operators execute remotely, and MCP based operators. 

## Operator Registry

To interface with operators you can use  the operator registry by creating an instance of operator registry. Once you have an instance, you can query operator servers, operators on a server, execute operators, etc., very much like using tool registry.

Below is an example:
```
from blue.operators.registry import OperatorRegistry

platform_id = "default"
operator_registry_id = "default"

prefix = 'PLATFORM:' + platform_id
registry = OperatorRegistry(id=operator_registry_id, prefix=prefix)

# get list of servers
operator_servers = registry.get_servers()

# get list of operators on a server
operators = registry.get_server_operators("blue_ray")

# search operators
registry.search_records("join tables", approximate=True, type="operator")

# get instance of a operator
operator = get_server_operator("blue_ray", "join")

# execute opertor
input_data = [
        [{"job_id": 1, "name": "name A", "salary": 100000}, {"job_id": 2, "name": "name B", "location": "state B", "salary": 200000}],
        [{"job_id": 2, "location": "city B"}, {"job_id": 3, "location": "city C"}],
        [{"id": 1, "title": "title A"}, {"id": 4, "title": "title D"}, {"id": 2, "title": "title B"}],
    ]

   
attributes = {"join_on": [["job_id"], ["job_id"], ["id"]], "join_type": "inner", "join_suffix": ["_employee", "_geometry", "_job_content"], "keep_keys": "left"}

kwargs = {"input_data": input_data, "attributes": attributes}
registry.execute_operator("join", "blue_ray", None, kwargs)
```


