###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.data.registry import DataRegistry
import traceback

###############
### Data Discover Operator


def data_discover_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
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

    # Get data registry from properties - follow agent pattern
    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
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
                search_results = search_method(search_query, type=concept_type, page=page, page_size=page_size)
            else:
                search_results = search_method(search_query, type=concept_type, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)

            for result in search_results:
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
                    search_results = search_method(search_query, type=concept_type, page=current_page, page_size=page_size)
                else:
                    search_results = search_method(search_query, type=concept_type, approximate=approximate, hybrid=hybrid, page=current_page, page_size=page_size)

                if len(search_results) == 0:
                    break

                for result in search_results:
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
        traceback.print_exc()
        return [[]]

    # limit results
    if limit >= 0:
        return [results[:limit]]
    else:
        return [results]


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
    """Validate data discover operator attributes."""
    try:
        if not default_operator_validator(input_data, attributes, properties):
            return False
    except Exception:
        return False

    # Check required attributes, the type of the attributes is validated by the default operator validator
    search_query = attributes.get('search_query', '')
    page = attributes.get('page', 0)
    page_size = attributes.get('page_size', 10)
    threshold = attributes.get('threshold', 0.5)

    if not search_query or not search_query.strip():
        return False
    if page < 0 or page_size <= 0:
        return False
    if threshold < 0 or threshold > 1:
        return False

    return True


def data_discover_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain data discover operator output."""
    concept_type = attributes.get('concept_type', 'source')
    use_hierarchical = attributes.get('use_hierarchical_search', True)
    search_method = "hierarchical" if use_hierarchical else "regular"

    data_discover_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"Data discover operator searched for {concept_type} entities using {search_method} search with query '{attributes.get('search_query', '')}' and returned {len(output[0]) if output and len(output) > 0 else 0} results.",
    }
    return data_discover_explanation


###############
### DataDiscoverOperator
#
class DataDiscoverOperator(Operator):
    """
    Data discover operator that searches for data sources
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
