import string
import base64
import re
import pydash
from jinja2 import Environment, BaseLoader
import re


def camel_case(string):
    words = string.split("_")
    return " ".join(word.capitalize() for word in words)


def safe_substitute(ts, **mappings):

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
    # Use regex to remove all non-alphanumeric characters
    cleaned_string = re.sub(r"[^a-zA-Z0-9 ]", "", input_string)
    cleaned_string = cleaned_string.replace(" ", "_")
    return cleaned_string


def encode_websafe_no_padding(data: str) -> str:
    if not pydash.is_empty(data):
        bytes_data = data.encode('utf-8')
        return base64.urlsafe_b64encode(bytes_data).decode("utf-8").rstrip('=')
    raise ValueError('Empty data')


def decode_websafe_no_padding(encoded_data: str) -> str:
    if not pydash.is_empty(encoded_data):
        """decodes a url-safe base64 string (with or without padding)."""
        missing_padding = len(encoded_data) % 4
        if missing_padding:
            encoded_data += '=' * (4 - missing_padding)
        decoded_bytes = base64.urlsafe_b64decode(encoded_data)
        return decoded_bytes.decode('utf-8')
    raise ValueError('Empty encoded_data')
