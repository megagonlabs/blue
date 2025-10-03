# Utils

Blue library has a number of utilities that help you develop agents, tools, services, and beyond. Below are some high-level information on each utility. 

Please refer to the API Doc for more details on each utility.

List of Utilities:
* Directed Acyclic Graph (DAG) Utils: Functions to create and manipulate DAGs
* JSON Utils: Functions to load, query, summarize, flatten, and beyond for JSON data
* Log Utils: Functions for creating logs with custom format and options
* Service Utils: Functions to map data for services (APIs) and post-processing responses
* Similarity Utils: Functions to compute a variety of similarity scores
* String Utils: Functions to process strings, substitutions, encoding safe strings
* Tool Utils: Functions to extract signatures, convert types for tool development
* Type Utils: Functions to manage and transform types
* UUID Utils: Generate create unique ids and process canonical ids

## Directed Acyclic Graph (DAG) Utils

This utility defines a base class (`Base`) that forms the core class for graph nodes, complete graphs, and plans. `Base` class allows users to set and get custom data through methods such as `set_data` and `get_data` as well as means to sycnrhonize them whenever there is a change in the data. Each instance of base object has an `id`, `type`, `label`, and a set of properties, set through methods such as `get_properties`, `set_property`, and `get_property`.

`Node` class extends `Base` to represent a node in the graph. As such it has specific data (e.g. `prev` and `next`) and methods to navigate the graph and connect nodes,  such as `connect_to`.

`Entity` class is just a special extension of `Base` class to represent entities that a graph `Node` represents. For example, a node might have a reference to an associated entity such as an agent.

`DAG` class extends `Base` class to represent a directed acyclic graph. As such it has methods to create nodes and connect nodes (e.g. `create_nodes`, `connect_nodes`), retrieve nodes (e.g. `get_node_by_id`, `get_node_by_label`), navigate graph (e.g. `get_prev_nodes`, `get_next_nodes`) and helper functions such as `filter_nodes`, `count_nodes`, `is_node_leaf`, etc.

`EntityDAG` class extends `DAG` to represent a special DAG, where nodes can optionally refer to entities, such as agents, operators. It has methods such as `create_entity`, `get_entities`, `get_entity_by_id`, `get_entity_by_label`, retrieve entities associated with nodes and vice versa, e.g. `get_nodes_by_entity`, `set_node_entity`, `get_node_entity`.

`Plan` class that extends `EntityDAG` with specific support for merging plans, through a `merge` function. 

## JSON Utils

This utility container helper functions to load and save json array (e.g. `load_json_array`, `save_json_array`), as well as query, set, and update json objects through json-path queries (e.g. `json_query`, `json_filter_array`, `json_query_set`, `json_query_update`), merging (`merge_json`) and summarizing json objects (`merge_json`).

## Log Utils

Mainly this log util defines a `CustomLogger` with specific custom options and data to record and report with custom formatting such as `JSON`, through methods such as `set_config_option`, `set_config_output`, `set_config_data`, set log level `setLevel` and report logs for different levels such as `debug`, `warn`, `info`, `error`, etc.
    
## Service Utils

## Similarity Utils

## String Utils

## Tool Utils

## Type Utils

## UUID Utils
