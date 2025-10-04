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

These utils aim agent, tool, and operators to easily interface with services, e.g. APIs. `ServiceClient` is a base class that is designed be the inteface to talk to an API. To support this it has a number of properties designed to construct a message to the API from input and other properties and parse response from the API to build the right output. Below are the properties to support this:

* `input_json` : Initializes input if JSON is the input format. When set to None, input is just text. Otherwise JSON is constructed from the value of this property and input is plugged in to the right place in the input json using below properties.

* `input_context`: Defines where in the input json input is plugged in using JSONPath.

* `input_context_field`: Defines the input field name where input is plugged in.

* `input_field`: Defines the input field of the API request. Input is set as the value of this property, as constructued from above process for constructing input.

* `input_template`: Defines the template of the input using a template. When set to None it is assumed that input is passed on without an additionally formatting. Otherwise, input_template is expected to be of the following format: .....{var1}....{input}....{var2}... where var1 and var2 is substituted from the corresponding properties of the agent, and input is coming from the input stream.

* `output_path`: Define where in the API response to find the output using JSONPath. For example, $.result would point to the result property in the response JSON.

* `output_template`: Defines the template of the output (in a similar fashion as in input_template using a template. When set to None it is assumed that output is returned without an additionally formatting. Otherwise, output_template is expected to be of the following format: .....{var1}....{output}....{var2}... where var1 and var2 is substituted from the corresponding properties of the agent, and output is coming from the response, extracted through output_path.

`ServiceClient` class also defines two methods that can be overried to suit for a specific API:

* `extract_input_params(input_data, properties=None)`: extracts input parameters, used for substitution later on, before API call
* `extract_output_params(output_data, properties=None)`: extracts output parameters, used for substitution, after API call
* `extract_api_properties(properties=None)`: extracts API related properties
* `create_message(input_data, properties=None, additional_data=None)`: creates message to send to the API 
* `create_output(response, properties=None)`: creates output from response
* `validate_input(input_data, properties=None)`: used before calling the API to make sure the input text is validated.
* `process_output(output_data, properties=None)`: used post-process output after a response from calling the API. By default `output_cast` is used to cast output from API but can be overriden to provide more complex post processing. Additonally basic transformations such as substitution and replacements can be done, using properties such as `output_strip`, `output_transformations`.
* `execute_api_call(input, properties=None, additional_data=None)`: 

## Similarity Utils

This util contains helper functions such as `compute_bm25_score`, `normalize_bm25_scores` and `compute_vector_score` to ease up the work of computing similarity scores, vectors, etc.

## String Utils

This utils contains helper function such as:

* `camel_case(string)`: Convert a string to Camel Case by splitting on underscores.
* `safe_substitute(ts, **mappings)`: Recursively substitute variables in a template string using both string.Template and Jinja2
* `remove_non_alphanumeric(input_string)`: Remove non-alphanumeric characters from a string, also replaces spaces with underscores
* `encode_websafe_no_padding(data: str) -> str`: Encoding for web safe string
* `decode_websafe_no_padding(encoded_data: str) -> str`: Decoding from web safe string 

## Tool Utils

## Type Utils

## UUID Utils
