###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.operators.registry import OperatorRegistry

import logging

###############
### Operator Discover Operator


def operator_discover_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
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

    # Get operator registry from properties
    operator_registry = _get_operator_registry_from_properties(properties)
    if not operator_registry:
        logging.info("No operator registry found!")
        return [[]]

    results = []

    try:
        # For non-approximate search OR when progressive pagination is disabled, use simple pagination
        if (not approximate and not hybrid) or not progressive_pagination:
            search_results = operator_registry.search_records(keywords=search_query, type='operator', approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)

            for result in search_results:
                transformed_result = {
                    'type': 'operator',
                    'name': result['name'],
                    'id': result['id'],
                    'scope': result['scope'],
                    'path': f"{result['scope']}/operator/{result['name']}",
                }
                if 'score' in result:
                    transformed_result['score'] = float(result['score'])

                full_record = operator_registry.get_record(result['name'], 'operator', result['scope'])
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
                search_results = operator_registry.search_records(keywords=search_query, type='operator', approximate=approximate, hybrid=hybrid, page=current_page, page_size=page_size)

                if len(search_results) == 0:
                    break

                for result in search_results:
                    # Check threshold for approximate/hybrid search
                    score = float(result['score'])
                    if score <= threshold:
                        transformed_result = {
                            'type': 'operator',
                            'name': result['name'],
                            'id': result['id'],
                            'scope': result['scope'],
                            'path': f"{result['scope']}/operator/{result['name']}",
                            'score': result['score'],
                        }

                        full_record = operator_registry.get_record(result['name'], 'operator', result['scope'])
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
        logging.info(traceback.format_exc())
        return [[]]

    # limit results
    if limit >= 0:
        return [results[:limit]]
    else:
        return [results]


def operator_discover_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate operator discover operator attributes."""
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


def operator_discover_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain operator discover operator output."""
    operator_discover_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"operator discover operator searched for operators with query '{attributes.get('search_query', '')}' and returned {len(output[0]) if output and len(output) > 0 else 0} results.",
    }
    return operator_discover_explanation


###############
### OperatorDiscoverOperator
#
class OperatorDiscoverOperator(Operator):
    """
    Operator discover operator that searches for operators

    Attributes:
    ----------
    | Name                   | Type  | Required | Default | Description                                                                                          |
    |------------------------|-------|----------|---------|------------------------------------------------------------------------------------------------------|
    | `search_query`           | str   | :fontawesome-solid-circle-check: {.green-check}     | ""      | Text to search for in operator names and descriptions                                               |
    | `approximate`            | bool  | :fontawesome-solid-circle-check: {.green-check}     | True    | Whether to use approximate (vector) search                                                          |
    | `hybrid`                 | bool  |     | False   | Whether to use hybrid search (text + vector)                                                        |
    | `limit`                  | int   |     | -1      | Max number of results to return (-1 = unlimited)                                                    |
    | `page`                   | int   |     | 0       | Page number for pagination                                                                          |
    | `page_size`              | int   |     | 10      | Number of results per page (default: 10, max: 100)                                                 |
    | `include_metadata`       | bool  |     | False   | Whether to include metadata in results (description and properties always included)                |
    | `threshold`              | float |     | 0.5     | Similarity threshold for filtering results (0.0-1.0, lower = more similar; applies to approximate/hybrid search) |
    | `progressive_pagination` | bool  |     | False   | Whether to use progressive pagination for approximate/hybrid search (searches all pages until threshold exceeded) |


    """

    PROPERTIES = {}

    name = "operator_discover"
    description = "Discovers operators using the operator registry"
    default_attributes = {
        "search_query": {"type": "str", "description": "Text to search for in operator names and descriptions", "required": True, "default": ""},
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
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=operator_discover_operator_function,
            description=description or self.description,
            properties=properties,
            validator=operator_discover_operator_validator,
            explainer=operator_discover_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###########
### Helper functions


def _get_operator_registry_from_properties(properties: Dict[str, Any] = None) -> Optional[OperatorRegistry]:
    """Get data registry from properties."""
    if not properties:
        return None

    if 'operator_registry' in properties and isinstance(properties['operator_registry'], OperatorRegistry):
        return properties['operator_registry']

    platform_id = properties.get("platform.name")
    operator_registry_id = properties.get("operator_registry.name")

    if platform_id and operator_registry_id:
        prefix = 'PLATFORM:' + platform_id
        return OperatorRegistry(id=operator_registry_id, prefix=prefix, properties=properties)

    return None
