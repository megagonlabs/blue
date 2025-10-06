import json
import re
import logging

import jsonpath_ng as jp
from jsonmerge import merge
import decimal


### json utility functions
## load json objects as an array from a file
def load_json_array(json_file, single=False):
    """Loads JSON objects from a file into an array.

    It builds JSON array by oncatenating lines until a complete JSON object is formed where bracket counts match for both curly and square brackets.

    Parameters:
        json_file: JSON file path
        single: If True, treats each line as a separate JSON object. Defaults to False.

    Returns:
        JSON array of objects
    """
    json_array = []
    with open(json_file) as fp:
        json_string = ''
        cb_count = 0
        sb_count = 0
        for line in fp:

            cb_count += line.count('{')
            sb_count += line.count('[')
            cb_count -= line.count('}')
            sb_count -= line.count(']')
            json_string += line

            if single:
                sb_count = 0
                cb_count = 0

            if sb_count == 0 and cb_count == 0:
                json_element = json.loads(json_string)
                json_array.append(json_element)
                json_string = ''
    return json_array


## save json objects as an array from a file
def save_json_array(file_path, json_array):
    """Saves JSON objects from an array to a file, one object per line.

    Parameters:
        file_path: File path to save JSON objects
        json_array: Array of JSON objects to save
    """
    with open(file_path, "w") as fp:
        for json_element in json_array:
            line = json.dumps(json_element)
            fp.write(line + "\n")


## jsonpath get
def json_query(json_object, json_path_query, single=True, default=None):
    """Query JSON object using JSONPath.

    Parameters:
        json_object: JSON object to query
        json_path_query: JSONPath query string
        single: If True, returns a single value. Defaults to True.
        default: Default value if no match is found. If None, returns None.

    Returns:
        Query results (single value or list of values)
    """
    jpq = jp.parse(json_path_query)

    match_values = [m.value for m in jpq.find(json_object)]

    r = match_values
    if single:
        r = match_values[0] if match_values else None

    if r == None:
        if default == None:
            return r
        else:
            return default
    else:
        return r


def json_filter_array(json_array, json_path_query, match_value, match=True):
    """Filter JSON array based on a JSONPath query and match value.

    Parameters:
        json_array: JSON object to query
        json_path_query: JSONPath query string
        match_value: Value to match against
        match: If True, keeps objects where the query result matches the match_value. If False, keeps objects where it does not match. Defaults to True.

    Returns:
        Filtered JSON array
    """
    filtered_array = []
    for json_object in json_array:
        value = json_query(json_object, json_path_query, single=True)
        if match:
            if match_value == value:
                filtered_array.append(json_object)
            else:
                continue
        else:
            if match_value != value:
                filtered_array.append(json_object)
            else:
                continue
    return filtered_array


def json_query_set(json_object, attribute, value, context='$'):
    """Set attribute value in JSON object using JSONPath context.

    Parameters:
        json_object: JSON object to update
        attribute: Attribute to set
        value: Value to set
        context: JSONPath query context. Defaults to '$'.

    """
    jpq = jp.parse(context)
    matches = jpq.find(json_object)
    for match in matches:
        if match.context is None:
            json_object[attribute] = value
        else:
            if type(match.value) is not dict:
                raise Exception('context must be a dict')
            if type(match.path) is jp.Index:
                match.context.value[match.path.index][attribute] = value
            else:
                for field in match.path.fields:
                    match.context.value[field][attribute] = value


def json_query_add(json_object, attribute, value, context='$', single=True):
    """Add value to attribute in JSON object using JSONPath context.

    Parameters:
        json_object: JSON object to update
        attribute: Attribute to add to
        value: Value to add
        context: JSONPath query context. Defaults to '$'.
        single: If True, adds value as a single element. If False, extends the list. Defaults to True.
    """
    json_query_update(json_object, attribute, lambda match: value, context=context, add=True, single=single)


def json_query_update(json_object, attribute, update_function, context='$', add=False, single=True):
    """Update attribute in JSON object using a function and JSONPath context.

    Parameters:
        json_object: JSON object to update
        attribute: Attribute to update
        update_function: Function that takes a match object and returns the new value
        context: JSONPath query context. Defaults to '$'.
        add: If True, adds the new value to the existing value. If False, replaces it. Defaults to False.
        single: If True, updates value as a single element. If False, extends the list. Defaults to True.
    """
    json_path_query = context + '.' + attribute
    jpq = jp.parse(json_path_query)
    matches = jpq.find(json_object)
    for match in matches:
        if type(match.path) is jp.Index:
            if add:
                match.context.value[match.path.index] = _add(match.context.value[match.path.index], update_function(match), single=single)
            else:
                match.context.value[match.path.index] = update_function(match)
        else:
            for field in match.path.fields:
                if add:
                    match.context.value[field] = _add(match.context.value[field], update_function(match), single=single)
                else:
                    match.context.value[field] = update_function(match)


def _add(target, value, single=True):
    t = target
    if type(target) is list:
        if type(value) is list:
            if single:
                return t + [value]
            else:
                return t + value
        else:
            if single:
                return t + [value]
            else:
                return t + [value]
                # raise Exception("{} is not a list".format(value))
    else:
        if type(value) is list:
            if single:
                for v in value:
                    t = t + v
                return t
                # raise Exception("{} cannot be added to {}".format(value, target))
            else:
                for v in value:
                    t = t + v
                return t
        else:
            if single:
                return t + value
            else:
                return t + value
                # raise Exception("{} is not a list".format(value))


def merge_json(original_json, update_json):
    """Merge two JSON objects.

    Parameters:
        original_json: Original JSON object
        update_json: JSON object to merge

    Returns:
        Merged JSON object
    """
    return merge(original_json, update_json)


def union_jsonarray_by_attribute(json_array_a, json_array_b, attr):
    """Computes the union of two JSON arrays based on a specified attribute.

    Parameters:
        json_array_a: JSON array A
        json_array_b: JSON array B
        attr: Attribute to base the union on

    Returns:
        Union of the two JSON arrays based on the specified attribute
    """
    m = {}
    for o in json_array_a:
        m[o[attr]] = o
    for o in json_array_b:
        m[o[attr]] = o

    return list(m.values())


## flatten json
def flatten_json(json_object, separator='___', num_marker='$$$', flattenList=False):
    """Flattens a nested JSON object into a single-level dictionary.

    Parameters:
        json_object: JSON object to flatten
        separator: Separator to use between nested keys. Defaults to '___'.
        num_marker: Marker to denote list indices. Defaults to '$$$'.
        flattenList: If True, flattens lists by including indices in keys. If False, keeps lists intact. Defaults to False.

    Returns:
        Flattened JSON object
    """
    result = {}

    def _flatten_recursively(x, prefix=''):
        if type(x) is dict:
            for a in x:
                _flatten_recursively(x[a], prefix + a + separator)
        elif type(x) is list:
            if flattenList:
                i = 0
                for a in x:
                    _flatten_recursively(a, prefix + num_marker + str(i) + num_marker + separator)
                    i += 1
            else:
                result[prefix[: -len(separator)]] = x
        else:
            result[prefix[: -len(separator)]] = x

    _flatten_recursively(json_object)
    return result


def unflatten_json(json_object, separator='___', num_marker='$$$', unflattenList=False):
    """Unflattens a flattened JSON object back into a nested structure.

    Parameters:
        json_object: Flattened JSON object to unflatten
        separator: Separator used between nested keys. Defaults to '___'.
        num_marker: Marker used to denote list indices. Defaults to '$$$'.
        unflattenList: If True, reconstructs lists from keys with indices.

    Returns:
        Nested JSON object
    """
    result = {}
    for a in json_object:
        v = json_object[a]
        al = a.split(separator)
        r = result
        prev_r = None
        prev_ali = None
        for i in range(0, len(al)):
            ali = al[i]
            alix = _is_list_index(ali, num_marker)
            is_index = type(alix) == int

            if is_index:
                if unflattenList:
                    if type(r) is dict:
                        if prev_r is None:
                            result = []
                            r = []
                        else:
                            prev_r[prev_ali] = []
                            r = prev_r[prev_ali]
            if i == len(al) - 1:
                if is_index:
                    if unflattenList:
                        if alix >= len(r):
                            r = r + [None] * (alix - len(r) + 1)
                            prev_r[prev_ali] = r
                            if prev_r is None:
                                result = r

                r[alix] = v
            else:
                if is_index:
                    if unflattenList:
                        if alix < len(r):
                            if r[alix] == None:
                                r[alix] = {}
                        else:
                            r = r + [None] * (alix - len(r) + 1)
                            r[alix] = {}
                            if prev_r is None:
                                result = r
                            else:
                                prev_r[prev_ali] = r
                    else:
                        if alix not in r:
                            r[alix] = {}
                else:
                    if alix not in r:
                        r[alix] = {}
                prev_r = r
                prev_ali = alix
                r = r[alix]
    return result


def tokenize_json(json_object, reserved_dict=None):
    """Tokenizes strings in a JSON object, replacing them with unique integer IDs.

    Parameters:
        json_object:  JSON object to tokenize
        reserved_dict: Dictionary of reserved tokens with their corresponding IDs. Defaults to None.

    Returns:
        Tuple of (tokenized JSON object, token to ID mapping, ID to token mapping)
    """

    token2id = {}
    id2token = {}

    if reserved_dict is None:
        reserved_dict = dict()

    def _tokenize_json_recursively(x, token2id, id2token):
        result = None
        if type(x) is dict:
            result = {}
            for a in x:
                result[a] = _tokenize_json_recursively(x[a], token2id, id2token)
        elif type(x) is list:
            result = []
            for a in x:
                ra = _tokenize_json_recursively(a, token2id, id2token)
                result.append(ra)
        elif type(x) is str:
            token = x
            if token in token2id:
                id = token2id[token]
            else:
                id = len(id2token)
                while id in reserved_dict:
                    token2id[reserved_dict[id]] = id
                    id2token[id] = reserved_dict[id]
                    id = len(id2token)
                token2id[token] = id
                id2token[id] = token
            result = id
        return result

    tokenized_json = _tokenize_json_recursively(json_object, token2id, id2token)

    for id in reserved_dict:
        token2id[reserved_dict[id]] = id
        id2token[id] = reserved_dict[id]

    return tokenized_json, token2id, id2token


def _is_list_index(s, num_marker='$$$'):
    try:
        if s[0 : len(num_marker)] != num_marker or s[len(s) - len(num_marker) :] != num_marker:
            return s
        else:
            s = s[len(num_marker) : len(s) - len(num_marker)]
        x = int(s)
        if x >= 0:
            return x
        else:
            return s
    except ValueError:
        return s


def safe_json_parse(text):
    """Handles cases where JSON is wrapped in ```json ... ```

    Parameters:
        text: Text to parse

    Returns:
        Parsed JSON object or empty dict on failure
    """
    if text is None:
        return {}

    # Remove markdown code block wrappers
    cleaned = re.sub(r"^```[a-zA-Z]*\n", "", text.strip())
    cleaned = re.sub(r"\n```$", "", cleaned.strip())

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logging.warning(f"Failed to parse JSON: {e}")
        return {}


def json_safe(obj):
    """Convert an object to a JSON-safe representation.

    Parameters:
        obj: Object to convert

    Returns:
        JSON-safe object
    """
    if isinstance(obj, decimal.Decimal):
        # Convert to int if whole number, else float
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    return obj


def summarize_json(data, depth=0, text_limit=100, depth_limit=3, list_limit=5, key_limit=5):
    """Summarizes a JSON object by truncating text, limiting depth, and restricting list and key counts.

    Parameters:
        data: JSON object to summarize
        depth: Current depth of summarization. Defaults to 0.
        text_limit: Maximum length of text strings. Defaults to 100.
        depth_limit: Maximum depth of nested structures. Defaults to 3.
        list_limit: Maximum number of list items to include. Defaults to 5.
        key_limit: Maximum number of object keys to include. Defaults to 5.

    Returns:
        Summarized JSON object
    """
    if depth > depth_limit:
        return "..."
    if not isinstance(data, (list, dict)):
        if isinstance(data, str):
            return data[:text_limit] + ("" if len(data) < text_limit else "...")
        return data
    if isinstance(data, list):
        return [summarize_json(item, depth=depth + 1, text_limit=text_limit, depth_limit=depth_limit, list_limit=list_limit, key_limit=key_limit) for item in data[:list_limit]]
    if isinstance(data, dict):
        all_keys = list(data.keys())
        kept_keys = all_keys[:key_limit]
        truncated_keys = all_keys[key_limit:]
        d = dict([(key, summarize_json(data[key], depth=depth + 1, text_limit=text_limit, depth_limit=depth_limit, list_limit=list_limit, key_limit=key_limit)) for key in kept_keys])
        if truncated_keys:
            d["_truncated_keys"] = truncated_keys
        return d
