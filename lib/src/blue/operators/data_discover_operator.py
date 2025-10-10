###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.data.registry import DataRegistry

###############
### Data Discover Operator


def data_discover_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Discover data sources using the data registry with search capabilities.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), not used for discovery.
        attributes: Dictionary containing search parameters including search_query, approximate, hybrid, pagination settings, and scope information.
        properties: Optional properties dictionary containing data registry information. Defaults to None.

    Returns:
        List containing discovered data sources matching the search criteria.
    """
    # Extract attributes
    search_query = attributes.get('search_query', '')
    approximate = attributes.get('approximate', True)
    hybrid = attributes.get('hybrid', False)
    limit = attributes.get('limit', -1)
    page = attributes.get('page', 0)
    page_size = attributes.get('page_size', 10)
    include_metadata = attributes.get('include_metadata', False)
    threshold = attributes.get('threshold', 0.5)
    progressive_pagination = attributes.get('progressive_pagination', False)
    concept_type = attributes.get('concept_type', 'source')
    use_hierarchical_search = attributes.get('use_hierarchical_search', True)
    scope = attributes.get('scope', None)
    source = attributes.get('source', None)
    database = attributes.get('database', None)
    collection = attributes.get('collection', None)
    auto_construct_scope = attributes.get('auto_construct_scope', True)
    filter_names = attributes.get('filter_names', [])

    search_scope = _construct_scope(scope, source, database, collection, concept_type, auto_construct_scope)

    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        logging.error("Error: Data registry not found")
        return [[]]

    results = []

    try:
        # Choose the search method based on use_hierarchical_search flag
        search_method = data_registry.search_records_hierarchical if use_hierarchical_search else data_registry.search_records

        # Determine if we should use simple pagination
        use_simple_pagination = (not approximate and not hybrid) or not progressive_pagination

        if use_simple_pagination:
            # Simple pagination - single call
            if use_hierarchical_search:
                search_results = search_method(search_query, type=concept_type, scope=search_scope, page=page, page_size=page_size)
            else:
                search_results = search_method(search_query, type=concept_type, scope=search_scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)

            for result in search_results:
                # filter names
                if result['name'] in filter_names:
                    continue

                transformed_result = _transform_result(result, concept_type, data_registry, include_metadata)

                # Apply threshold filtering for approximate/hybrid search even in simple pagination mode
                if (approximate or hybrid) and 'score' in result:
                    score = float(result['score'])
                    if score <= threshold:
                        results.append(transformed_result)
                else:
                    results.append(transformed_result)
        else:
            # Progressive pagination - loop until threshold exceeded
            current_page = page

            while True:
                if use_hierarchical_search:
                    search_results = search_method(search_query, type=concept_type, scope=search_scope, page=current_page, page_size=page_size)
                else:
                    search_results = search_method(search_query, type=concept_type, scope=search_scope, approximate=approximate, hybrid=hybrid, page=current_page, page_size=page_size)

                if len(search_results) == 0:
                    break

                for result in search_results:
                    # filter names
                    if result['name'] in filter_names:
                        continue

                    # Check threshold for approximate/hybrid search
                    score = float(result['score'])
                    if score <= threshold:
                        transformed_result = _transform_result(result, concept_type, data_registry, include_metadata)
                        results.append(transformed_result)
                    else:
                        # Score exceeds threshold, stop searching
                        break

                # Check if last result exceeded threshold to break outer loop
                if len(search_results) > 0:
                    last_score = float(search_results[-1]['score'])
                    if last_score > threshold:
                        break

                # Move to next page
                current_page += 1

    except Exception as e:
        logging.error(traceback.format_exc())
        return [[]]

    # limit results
    if limit >= 0:
        return [results[:limit]]
    else:
        return [results]


def _construct_scope(scope, source, database, collection, concept_type, auto_construct=True):
    """Construct search scope from attributes based on data registry hierarchy."""
    if scope is None:
        # TODO: this might need adjustment after finalizing what does scope mean, exact scope or parent/prefix scope, and whether it's required to construct a scope for None if source/database/collection are provided.
        return None

    # If auto_construct is False, return the scope as-is
    if not auto_construct:
        return scope.rstrip('/') if scope else "/"

    # If explicit scope is provided and not default, use it as base
    if scope and scope != "/":
        base_scope = scope.rstrip('/')
    else:
        base_scope = "/"
        if source:
            base_scope = f"/source/{source}"
            if database:
                base_scope = f"/source/{source}/database/{database}"
                if collection:
                    base_scope = f"/source/{source}/database/{database}/collection/{collection}"

    # Parse the base scope to extract components
    scope_parts = base_scope.split('/')
    scope_components = {'source': None, 'database': None, 'collection': None, 'entity': None, 'relation': None, 'attribute': None}

    # Extract components from scope path
    for i, part in enumerate(scope_parts):
        if part == 'source' and i + 1 < len(scope_parts):
            scope_components['source'] = scope_parts[i + 1]
        elif part == 'database' and i + 1 < len(scope_parts):
            scope_components['database'] = scope_parts[i + 1]
        elif part == 'collection' and i + 1 < len(scope_parts):
            scope_components['collection'] = scope_parts[i + 1]
        elif part == 'entity' and i + 1 < len(scope_parts):
            scope_components['entity'] = scope_parts[i + 1]
        elif part == 'relation' and i + 1 < len(scope_parts):
            scope_components['relation'] = scope_parts[i + 1]
        elif part == 'attribute' and i + 1 < len(scope_parts):
            scope_components['attribute'] = scope_parts[i + 1]

    if source:
        scope_components['source'] = source
    if database:
        scope_components['database'] = database
    if collection:
        scope_components['collection'] = collection

    # Construct the appropriate scope based on concept_type
    if concept_type == 'source':
        return "/"
    elif concept_type == 'database':
        if scope_components['source']:
            return f"/source/{scope_components['source']}"
        return "/"
    elif concept_type == 'collection':
        if scope_components['source'] and scope_components['database']:
            return f"/source/{scope_components['source']}/database/{scope_components['database']}"
        elif scope_components['source']:
            return f"/source/{scope_components['source']}"
        return "/"
    elif concept_type in ['entity', 'relation']:
        if scope_components['source'] and scope_components['database'] and scope_components['collection']:
            return f"/source/{scope_components['source']}/database/{scope_components['database']}/collection/{scope_components['collection']}"
        elif scope_components['source'] and scope_components['database']:
            return f"/source/{scope_components['source']}/database/{scope_components['database']}"
        elif scope_components['source']:
            return f"/source/{scope_components['source']}"
        return "/"
    elif concept_type == 'attribute':
        if scope_components['source'] and scope_components['database'] and scope_components['collection'] and scope_components['entity']:
            return f"/source/{scope_components['source']}/database/{scope_components['database']}/collection/{scope_components['collection']}/entity/{scope_components['entity']}"
        elif scope_components['source'] and scope_components['database'] and scope_components['collection'] and scope_components['relation']:
            return f"/source/{scope_components['source']}/database/{scope_components['database']}/collection/{scope_components['collection']}/relation/{scope_components['relation']}"
        elif scope_components['source'] and scope_components['database'] and scope_components['collection']:
            return f"/source/{scope_components['source']}/database/{scope_components['database']}/collection/{scope_components['collection']}"
        elif scope_components['source'] and scope_components['database']:
            return f"/source/{scope_components['source']}/database/{scope_components['database']}"
        elif scope_components['source']:
            return f"/source/{scope_components['source']}"
        return "/"
    else:
        # Fallback to base scope for unknown concept types
        return base_scope


def _transform_result(result, concept_type, data_registry, include_metadata):
    """Transform a search result into the expected format."""
    transformed_result = {
        'type': concept_type,
        'name': result['name'],
        'id': result['id'],
        'scope': result['scope'],
    }
    if 'score' in result:
        transformed_result['score'] = float(result['score'])

    full_record = data_registry.get_record(result['name'], concept_type, result['scope'])
    if full_record:
        transformed_result['description'] = full_record.get('description', '')
        transformed_result['properties'] = full_record.get('properties', {})
        if include_metadata:
            transformed_result['metadata'] = full_record.get('metadata', {})
    else:
        transformed_result['description'] = ''
        transformed_result['properties'] = {}

    return transformed_result


def data_discover_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate data discover operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    try:
        if not default_operator_validator(input_data, attributes, properties):
            return False
    except Exception:
        return False

    search_query = attributes.get('search_query', '')
    page = attributes.get('page', 0)
    page_size = attributes.get('page_size', 10)
    threshold = attributes.get('threshold', 0.5)
    source = attributes.get('source', None)
    database = attributes.get('database', None)
    collection = attributes.get('collection', None)

    if not search_query or not search_query.strip():
        return False
    if page < 0 or page_size <= 0:
        return False
    if threshold < 0 or threshold > 1:
        return False

    if database and not source:
        return False
    if collection and (not source or not database):
        return False

    concept_type = attributes.get('concept_type', 'source')
    valid_concept_types = ['source', 'database', 'collection', 'entity', 'relation', 'attribute']
    if concept_type not in valid_concept_types:
        return False

    return True


def data_discover_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for data discover operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the data discovery operation.
    """
    concept_type = attributes.get('concept_type', 'source')
    use_hierarchical = attributes.get('use_hierarchical_search', True)
    search_method = "hierarchical" if use_hierarchical else "regular"

    # Get scope information
    scope = attributes.get('scope', None)
    source = attributes.get('source', None)
    database = attributes.get('database', None)
    collection = attributes.get('collection', None)
    auto_construct_scope = attributes.get('auto_construct_scope', True)
    search_scope = _construct_scope(scope, source, database, collection, concept_type, auto_construct_scope)

    scope_info = f" within scope '{search_scope}'" if search_scope != '/' else ""

    data_discover_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"Data discover operator searched for {concept_type} entities using {search_method} search with query '{attributes.get('search_query', '')}'{scope_info} and returned {len(output[0]) if output and len(output) > 0 else 0} results.",
    }
    return data_discover_explanation


###############
### DataDiscoverOperator
#
class DataDiscoverOperator(Operator):
    """
     Data discover operator that searches for data sources

    Attributes:
    ----------
    | Name                   | Type   | Required | Default | Description |
    |-------------------------|--------|-----------|----------|--------------|
    | `search_query`          | str    | :fontawesome-solid-circle-check: {.green-check}    | ""       | Text to search for in source names and descriptions. |
    | `approximate`           | bool   | :fontawesome-solid-circle-check: {.green-check}    | True     | Whether to use approximate (vector) search. |
    | `hybrid`                | bool   |    | False    | Whether to use hybrid search (text + vector). |
    | `limit`                 | int    |    | -1       | Max number of results to return (-1 means unlimited). |
    | `page`                  | int    |    | 0        | Page number for pagination. |
    | `page_size`             | int    |    | 10       | Number of results per page (default: 10, max: 100). |
    | `include_metadata`      | bool   |    | False    | Whether to include metadata in results (description and properties always included). |
    | `threshold`             | float  |    | 0.5      | Similarity threshold for filtering results (0.0–1.0, lower = more similar, only applies to approximate/hybrid search). |
    | `progressive_pagination`| bool   |    | False    | Whether to use progressive pagination for approximate/hybrid search (searches all pages until threshold exceeded). |
    | `concept_type`          | str    |    | "source" | Record type to search for (e.g., 'source', 'database', 'collection', 'entity', 'attribute', 'relation'). |
    | `use_hierarchical_search` | bool |    | True     | Whether to use hierarchical search or regular search. |
    | `scope`                 | str    |      | None     | Search scope to limit results. |
    | `source`                | str    |      | None     | Source name to limit search scope. |
    | `database`              | str    |      | None     | Database name to limit search scope (requires source). |
    | `collection`            | str    |      | None     | Collection name to limit search scope (requires source and database). |
    | `auto_construct_scope`  | bool   |      | True     | Whether to auto-construct scope from individual attributes or use scope as-is. |
    | `filter_names`          | list   |      | []       | Filter out results with matching names in the filter list. |

    """

    PROPERTIES = {}

    name = "data_discover"
    description = "Discovers data sources using the data registry"
    default_attributes = {
        "search_query": {"type": "str", "description": "Text to search for in source names and descriptions", "required": True, "default": ""},
        "approximate": {"type": "bool", "description": "Whether to use approximate (vector) search", "required": True, "default": True},
        "hybrid": {"type": "bool", "description": "Whether to use hybrid search (text + vector)", "required": False, "default": False},
        "limit": {"type": "int", "description": "Max number of results to return (-1, unlimited)", "required": False, "default": -1},
        "page": {"type": "int", "description": "Page number for pagination", "required": False, "default": 0},
        "page_size": {"type": "int", "description": "Number of results per page (default: 10, max: 100)", "required": False, "default": 10},
        "include_metadata": {"type": "bool", "description": "Whether to include metadata in results (description and properties always included)", "required": False, "default": False},
        "threshold": {
            "type": "float",
            "description": "Similarity threshold for filtering results (0.0-1.0, lower = more similar, only applies to approximate/hybrid search)",
            "required": False,
            "default": 0.5,
        },
        "progressive_pagination": {
            "type": "bool",
            "description": "Whether to use progressive pagination for approximate/hybrid search (searches all pages until threshold exceeded)",
            "required": False,
            "default": False,
        },
        "concept_type": {
            "type": "str",
            "description": "Record type to search for (e.g., 'source', 'database', 'collection', 'entity', 'attribute', 'relation')",
            "required": False,
            "default": "source",
        },
        "use_hierarchical_search": {"type": "bool", "description": "Whether to use hierarchical search or regular search", "required": False, "default": True},
        "scope": {"type": "str", "description": "Search scope to limit results", "required": False, "default": None},
        "source": {"type": "str", "description": "Source name to limit search scope", "required": False, "default": None},
        "database": {"type": "str", "description": "Database name to limit search scope (requires source)", "required": False, "default": None},
        "collection": {"type": "str", "description": "Collection name to limit search scope (requires source and database)", "required": False, "default": None},
        "auto_construct_scope": {"type": "bool", "description": "Whether to auto-construct scope from individual attributes or use scope as-is", "required": False, "default": True},
        "filter_names": {"type": "list", "description": "Filter out results with matching names in the filter list", "required": False, "default": []},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=data_discover_operator_function,
            description=description or self.description,
            properties=properties,
            validator=data_discover_operator_validator,
            explainer=data_discover_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###########
### Helper functions


def _get_data_registry_from_properties(properties: Dict[str, Any] = None) -> Optional[DataRegistry]:
    """Get data registry from properties."""
    if not properties:
        return None

    if 'data_registry' in properties and isinstance(properties['data_registry'], DataRegistry):
        return properties['data_registry']

    platform_id = properties.get("platform.name")
    data_registry_id = properties.get("data_registry.name")

    if platform_id and data_registry_id:
        prefix = 'PLATFORM:' + platform_id
        return DataRegistry(id=data_registry_id, prefix=prefix, properties=properties)

    return None
