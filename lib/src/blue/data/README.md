# Data Sources and Processing

In blue there are several data related 

## Data Sources

## Data Registry



### Synchronization

### Stats

### Enrichment

## Data Pipeline

Data pipeline (`DataPipeline`)  is essentially a configuration of a set of operators to perform data related functions including discovery, retrieval, and transformation. Data pipeline is organized as a DAG, directed acyclic graph of operators.

Below is a simple example of a pipeline with a single operator, receiving data from input:
```
from blue.data.pipeline import DataPipeline, NodeType, EntityType, Status

# create data pipeline
p = DataPipeline()

# initialize input data
input_data = [
    [{"job_id": 1, "name": "name A", "salary": 100000}, {"job_id": 2, "name": "name B", "location": "state B", "salary": 200000}],
    [{"job_id": 2, "location": "city B"}, {"job_id": 3, "location": "city C"}],
    [{"id": 1, "title": "title A"}, {"id": 4, "title": "title D"}, {"id": 2, "title": "title B"}],
]

# define input node
i = p.define_input(value=input_data, provenance="$")

# initialize operator attribute
attributes = {"join_on": [["job_id"], ["job_id"], ["id"]], "join_type": "inner", "join_suffix": ["_employee", "_geometry", "_job_content"], "keep_keys": "left"}

# define join operator
o = p.define_operator("/server/blue_ray/operator/join", attributes=attributes)

# define output
r = p.define_output()

# set plan input / output
p.set_plan_input(i)
p.set_plan_output(r)

# connect input to operator to output
p.connect_nodes(i, o)
p.connect_nodes(o, r)
```

## Data Planner

```
import logging
logging.getLogger().setLevel(logging.INFO)

from blue.data.planner import DataPlanner, TaskType
from blue.data.pipeline import DataPipeline

properties = {
    "db.host": "blue_db_redis",
    "platform.name": "default",
    "operator_registry.name": "default",
    "data_registry.name": "default",
    "plan_discover_operator": "/server/blue_ray/operator/plan_discover",
}
query = "what management positions are available in the southern part of singapore?"
dp = DataPlanner(id="test", properties=properties)
plan = dp.plan(query, TaskType.QUESTION_ANSWER, {})
dp.execute(plan)
```

