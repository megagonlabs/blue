import string
import base64
import re
import pydash
from jinja2 import Environment, BaseLoader
import re


def camel_case(string):
    """
    Convert a string to Camel Case by splitting on underscores and capitalizing each word.

    Parameters:
        string (str): The input string to be converted.

    Returns:
        (str): The converted Camel Case string.
    """
    words = string.split("_")
    return " ".join(word.capitalize() for word in words)


def safe_substitute(ts, **mappings):
    """
    Recursively substitute variables in a template string using both string.Template and Jinja2.

    Parameters:
        ts (str): The template string containing placeholders.
        **mappings: Key-value pairs for substitution.

    Returns:
        The string with all placeholders substituted.
    """
    ## basic string template first
    t = string.Template(ts)
    r = t.safe_substitute(**mappings)

    ## jinja
    e = Environment(loader=BaseLoader()).from_string(r)
    r = e.render(**mappings)

    if r == ts:
        return r
    else:
        return safe_substitute(r, **mappings)


def remove_non_alphanumeric(input_string):
    """Remove non-alphanumeric characters from a string, also replaces spaces with underscores.

    Parameters:
        input_string (str): input string to be cleaned

    Returns:
        (str): Cleaned string with only alphanumeric characters and underscores.
    """
    # Use regex to remove all non-alphanumeric characters
    cleaned_string = re.sub(r"[^a-zA-Z0-9 ]", "", input_string)
    cleaned_string = cleaned_string.replace(" ", "_")
    return cleaned_string


def encode_websafe_no_padding(data: str) -> str:
    """Encodes a string to a url-safe base64 string without padding.

    Parameters:
        data: input string to be encoded

    Raises:
        ValueError: If the input data is empty.

    Returns:
        Url-safe base64 encoded string without padding.
    """
    if not pydash.is_empty(data):
        bytes_data = data.encode('utf-8')
        return base64.urlsafe_b64encode(bytes_data).decode("utf-8").rstrip('=')
    raise ValueError('Empty data')


def decode_websafe_no_padding(encoded_data: str) -> str:
    """Decodes a url-safe base64 string without padding.

    Parameters:
        encoded_data:  input url-safe base64 string to be decoded

    Raises:
        ValueError:  If the input encoded_data is empty.

    Returns:

    """
    if not pydash.is_empty(encoded_data):
        """decodes a url-safe base64 string (with or without padding)."""
        missing_padding = len(encoded_data) % 4
        if missing_padding:
            encoded_data += '=' * (4 - missing_padding)
        decoded_bytes = base64.urlsafe_b64decode(encoded_data)
        return decoded_bytes.decode('utf-8')
    raise ValueError('Empty encoded_data')
