import string
from jinja2 import Environment, BaseLoader

def camel_case(string):
    words = string.split("_")
    return " ".join(word.capitalize() for word in words)


def safe_substitute(ts, **mappings):
    
    ## basis string template first
    t = string.Template(ts)
    r = t.safe_substitute(**mappings)

    ## jinha
    ts = r 
    e = Environment(loader=BaseLoader()).from_string(ts)
    r = e.render(**mappings)
    
    if r == ts:
        return r
    else:
        return safe_substitute(r, **mappings)