import string
from jinja2 import Environment, BaseLoader

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