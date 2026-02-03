# Data Sources and Processing

Data is core to blue architecture as such blue has a number of abstractions to represent data of various modalities and granularity, to represent and execute data processing pipelines, and to plan data operations. 

## Data Entities

In blue `DataSource` is the top level data entity. It typically represents an instance of a database server, for example a Postgres DB server, MongoDB server, etc. Blue currently has support for relational databases such as postgres (`PostgresDBSource`), mysql (`MySQLDBSource`), and sqlite (`SQLiteDBSource`), semi-structured documents stores such as mongodb (`MongoDBSource`), graph databases such as neo4j (`NEO4JSource`), and an LLM-based data source such as (`OpenAISource`).

The structure of the various data entities across of different sources is:

- `DataSource` (e.g. MongoDB instance, Postgres Instance)
   - `Database` (e.g. MongoDB Database, Postgres Database)
      - `Collection` (e.g. MongoDB Collection, Postgres Schema)
         - `Entity` (e.g. MongoDB JSON Object, Postgres Table)
            - `Attribute` (e.g. MongoDB Attribute, Postgres Column)
         - `Relation` (e.g. MongoDB Attribute with JSON Object value, Postgres Tables with primary/foreign keys)
            - `Attribute` (e.g. MongoDB Attribute, Postgres Column)

## Data Registry

In the data registry any data entity has metadata such as `name`, `type`, `scope`, `description`, `properties` and `contents`. `properties` includes various metadata such as statistics, etc. For an attribute, properties also include various metadata about attribute values such as `value_semantics`, `semantic_discovery`, `semantic_roles`, `semantic_roles`, `value_axis`. `contents` is for entities under the hierarchy.


### Synchronization

In the data registry you can at any point synchronize a data entity. As a result of synchronization, the contents of the data entity is updated recursively. For example, for a postgres schema, tables in that schema are fetched, and then for each table, columns, etc. As such synchronization makes sure the content in the registry reflects what is in the data source, database, etc.

### Stats

You can collect stats about any data entity. For example, for an entity (e.g. postgres table) stats include `row_count`, `row_samples`. For an attribute stats collected includes `distinct_count`, `null_count`, `sample_values`, `min`, `max`, `most_common_vals`, etc. These stats can be utilized by any agent (or component) to make choices for example, nl2sql can use them to enrich context for sql translation.

### Enrichment

While you can manually write descriptions for any data entity, beyond the top levels, this quickly becomes very cumbersome. Automatic enrichment helps in these cases to use LLMs to write descriptions. You can enrich data entities at any level in the data registry.

Crucially, enrichment in Blue goes far beyond generating natural-language descriptions. 
It enriches attributes and entities with structured value semantics, turning raw schema into machine-interpretable metadata that agents can reason over.
Specifically, enrichment operates at the attribute level and incrementally infers and attaches:

**Value Semantics (VSI)** (attribute-level)
A bounded, deterministic classification of what the values are, inferred from statistics, sample values, and weak cross-attribute context (e.g., CURRENCY_AMOUNT, DURATION, ENUM_CATEGORY, ID_STRING).
This inference is explicitly value-centric and avoids domain or business assumptions.

**Semantic Discovery (SDI)** (attribute-level)
Open-world, fuzzy semantic signals that capture emergent patterns not covered by fixed taxonomies (e.g., latent categories, thresholds, or value groupings). 

**Domain Concepts** (attribute-level)
Canonical domain meanings inferred by mapping value semantics and semantic discovery signals onto a user-provided concept taxonomy (e.g., CONCEPT.LOCATION.CITY, CONCEPT.JOB_TITLE, CONCEPT.SKILL).
Domain concept mapping is taxonomy-driven and optional; if no taxonomy is provided, attributes default to CONCEPT.UNKNOWN.

Domain concept mapping relies on a concept taxonomy file supplied by the user. This file is not created automatically during Blue installation.
If it does not exist, domain concept mapping is skipped and attributes default to CONCEPT.UNKNOWN.

**Default taxonomy path**

By default, Blue looks for the taxonomy at:

/blue_data/config/concept_taxonomy.json

**Providing a Concept Taxonomy**

Users must create and supply the taxonomy file using one of the following methods.

**Option 1:** Override via configuration (recommended)

Provide a custom taxonomy path when initializing the metadata service:

MetaData(properties={
    "concept_taxonomy_path": "/path/to/my_concept_taxonomy.json"
})

**Option 2:** Create the default path manually

Create /blue_data/config/concept_taxonomy.json

Here is an example minimal concept taxonomy.json for HR domain. 

{ "version": "1.0", "concepts": [ "CONCEPT.LOCATION.STATE", "CONCEPT.LOCATION.CITY", "CONCEPT.LOCATION.COUNTRY", "CONCEPT.COMPENSATION.SALARY", "CONCEPT.COMPENSATION.RATE", "CONCEPT.CANDIDATE.EXPERIENCE", "CONCEPT.CANDIDATE.START_DATE", "CONCEPT.CANDIDATE.END_DATE", "CONCEPT.JOB.TITLE", "CONCEPT.SKILL.NAME", "CONCEPT.ID", "CONCEPT.DATE", "CONCEPT.TEXT", "CONCEPT.UNKNOWN" ] }





**Interpretive Semantics (IVS)** (attribute-level)
Optional ordinal or tiered interpretations for categorical attributes when strongly supported by evidence (e.g., severity levels, ordered tiers), with strict confidence and safety gating.

**Value Axes** (attribute-level)
Explicit comparative structure over values—continuous (e.g., magnitude-based numeric axes) or ordinal—derived from distributions or promoted from high-confidence interpretive semantics.
These axes capture extremes, thresholds, and polarity (e.g., “large vs. small”, “high vs. low”).

**Semantic Links** (entity-level)
Data-driven relationships between attributes (e.g., SEGMENTS, DERIVES, SUPPORTS), inferred using both column-level statistics and row-aligned co-occurrence evidence, and validated with semantic type constraints.

**Semantic Roles** (attribute-level)
Functional analytical roles (e.g., IDENTIFIER, EVENT_TIME, SEGMENTATION_DRIVER, EVIDENCE) inferred from value semantics and semantic links, rather than from schema names alone.

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

## Data Planner (*EXPERIMENTAL*)

Data planner allows automatic pipeline generation. As an experimental feature currently limited generation capabilities exist. 

Below is an example use of DataPlanner:

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

Executing the above plan should return:
```
{
  "$.db62c764.4acfc7b5.26999072.b664eab2.d479729c.f422fbd8.a4804c5b": [
    [
      {
        "job_title": "head of sales operations and capability",
        "company_name": "MONDELEZ ASIA PACIFIC PTE. LTD.",
        "location": "harbourfront"
      },
      {
        "job_title": "senior manager",
        "company_name": "Company Undisclosed",
        "location": "harbourfront"
      },
      {
        "job_title": "director of food & beverage",
        "company_name": "THE SINGAPORE RESORT & SPA",
        "location": "harbourfront"
      },
      {
        "job_title": "senior commissioning and qualification engineers",
        "company_name": "COMMISSIONING AGENTS INTERNATIONAL SINGAPORE, PTE. LTD.",
        "location": "harbourfront"
      },
      {
        "job_title": "quality assurance director",
        "company_name": "THE SINGAPORE RESORT & SPA",
        "location": "harbourfront"
      },
      {
        "job_title": "assistant director",
        "company_name": "RESORTS WORLD AT SENTOSA PTE. LTD.",
        "location": "harbourfront"
      },
      {
        "job_title": "regulatory portfolio lead",
        "company_name": "SYNGENTA ASIA PACIFIC PTE. LTD.",
        "location": "harbourfront"
      },
      {
        "job_title": "director of spa",
        "company_name": "THE SINGAPORE RESORT & SPA",
        "location": "harbourfront"
      },
      {
        "job_title": "shift manager",
        "company_name": "PEZZO SINGAPORE PTE. LTD.",
        "location": "harbourfront"
      },
      {
        "job_title": "senior financial analyst",
        "company_name": "HP PPS ASIA PACIFIC PTE. LTD.",
        "location": "harbourfront"
      }
    ]
  ],
  "$.db62c764.73ef013e": [
    []
  ]
}
```

The results indicate that two alternative pipelines were generated (`$.db62c764.73ef013e` denotes the provenance in the DAG) and one of them yields no resutls, while the other one produced the above list of entities.

To examine the generated plan further you can get the plan using:
```
plan.get_data()
```

Note that based on the properties of `DataPlanner` and the various operators, and the data sources used in the pipeline, execution of an automatically generated plan might yield different results (or no results at all). 
