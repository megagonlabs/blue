import typing
import inspect
from typing import List
from typing import Dict

from blue.utils import json_utils


def annotation_to_type_str(annotation):
    """Used to convert inspect annotations to type strings

    Parameters:
        annotation: Inspect annotation

    Returns:
        (str): Type string
    """
    if type(annotation) == type:
        if annotation == inspect._empty:
            return "unknown"
        else:
            return annotation.__name__
    else:
        type_str = str(annotation)
        type_str = type_str.replace("typing.", "")
        return type_str


def extract_signature(f, mcp_format=False):
    """Extracts the signature of a function and returns it as a dictionary.

    Parameters:
        f (callable): Function to extract signature from
        mcp_format (bool): If True, converts types to MCP format. Defaults to False.

    Returns:
        (dict): Dictionary containing function parameters and return type.
    """
    signature = inspect.signature(f)
    inspection = {}
    inspection["parameters"] = {}
    ps = signature.parameters.items()
    for pi in ps:
        k, p = pi
        ki = {}
        ki['type'] = annotation_to_type_str(p.annotation)
        if mcp_format:
            ki = json_utils.merge_json(ki, convert_type_string_to_mcp(ki['type']))
        default = p.default
        if default == inspect._empty:
            default = None
        if default:
            ki['required'] = False
            ki['default'] = default
        else:
            ki['required'] = True
        inspection["parameters"][k] = ki
    ri = signature.return_annotation
    r = {}
    if ri is not None:
        r['type'] = annotation_to_type_str(ri)
        if mcp_format:
            r = json_utils.merge_json(r, convert_type_string_to_mcp(r['type']))
    inspection["returns"] = r
    return inspection


def convert_type_string_to_mcp(type_str):
    """Converts a type string to MCP format.

    Parameters:
        type_str (str): Type string to convert

    Returns:
        (dict): MCP format dictionary
    """
    if type_str == "":
        return {"type": "unknown"}
    if type_str.lower() == "int" or type_str.lower() == "float":
        return {"type": "number"}
    elif type_str.lower() == "str":
        return {"type": "string"}
    elif type_str.lower().find("list") == 0:
        return {"type": "array", "items": convert_type_string_to_mcp(type_str[len("List") + 1 : -1])}
    elif type_str.lower().find("dict") == 0:
        return {"type": "object", "properties": {}}
    else:
        return {"type": "unknown"}
