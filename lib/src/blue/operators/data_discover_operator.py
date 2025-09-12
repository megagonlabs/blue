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
    page = attributes.get('page', 0)
    page_size = attributes.get('page_size', 10)
    include_metadata = attributes.get('include_metadata', False)
    threshold = attributes.get('threshold', 0.5)
    progressive_pagination = attributes.get('progressive_pagination', False)

    # Get data registry from properties - follow agent pattern
    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        return [[]]

    results = []

    try:
        # For non-approximate search OR when progressive pagination is disabled, use simple pagination
        if (not approximate and not hybrid) or not progressive_pagination:
            search_results = data_registry.search_records(search_query, type='source', approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)

            for result in search_results:
                transformed_result = {
                    'type': 'source',
                    'name': result['name'],
                    'id': result['id'],
                    'scope': result['scope'],
                    'path': f"/source/{result['name']}",
                }
                if 'score' in result:
                    transformed_result['score'] = float(result['score'])

                full_record = data_registry.get_record(result['name'], 'source', '/')
                if full_record:
                    transformed_result['description'] = full_record.get('description', '')
                    transformed_result['properties'] = full_record.get('properties', {})
                    if include_metadata:
                        transformed_result['metadata'] = full_record.get('metadata', {})
                else:
                    transformed_result['description'] = ''
                    transformed_result['properties'] = {}

                # Apply threshold filtering for approximate/hybrid search even in simple pagination mode
                if (approximate or hybrid) and 'score' in result:
                    score = float(result['score'])
                    if score <= threshold:
                        results.append(transformed_result)
                else:
                    results.append(transformed_result)

        else:
            # For approximate/hybrid search with progressive pagination enabled
            current_page = page

            while True:
                search_results = data_registry.search_records(search_query, type='source', approximate=approximate, hybrid=hybrid, page=current_page, page_size=page_size)

                if len(search_results) == 0:
                    break

                for result in search_results:
                    # Check threshold for approximate/hybrid search
                    score = float(result['score'])
                    if score <= threshold:
                        transformed_result = {
                            'type': 'source',
                            'name': result['name'],
                            'id': result['id'],
                            'scope': result['scope'],
                            'path': f"/source/{result['name']}",
                            'score': result['score'],
                        }

                        full_record = data_registry.get_record(result['name'], 'source', '/')
                        if full_record:
                            transformed_result['description'] = full_record.get('description', '')
                            transformed_result['properties'] = full_record.get('properties', {})
                            if include_metadata:
                                transformed_result['metadata'] = full_record.get('metadata', {})
                        else:
                            transformed_result['description'] = ''
                            transformed_result['properties'] = {}

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

    return [results]


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
    data_discover_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"Data discover operator searched for data sources with query '{attributes.get('search_query', '')}' and returned {len(output[0]) if output and len(output) > 0 else 0} results.",
    }
    return data_discover_explanation


###############
### DataDiscoverOperator
#
class DataDiscoverOperator(Operator):
    """
    Data discover operator that searches for data sources
    """

    PROPERTIES = {
        "tool_type": "operator",
        "platform.name": "default",
        "data_registry.name": "default",
    }

    name = "data_discover"
    description = "Discovers data sources using the data registry"
    default_attributes = {
        "search_query": {"type": "str", "description": "Text to search for in source names and descriptions", "required": True, "default": ""},
        "approximate": {"type": "bool", "description": "Whether to use approximate (vector) search", "required": True, "default": True},
        "hybrid": {"type": "bool", "description": "Whether to use hybrid search (text + vector)", "required": False, "default": False},
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
