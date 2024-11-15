import string

def camel_case(string):
    words = string.split("_")
    return " ".join(word.capitalize() for word in words)


def safe_substitute(ts, **mappings):
    t = string.Template(ts)
    r = t.safe_substitute(**mappings)
    if r == ts:
        return r
    else:
        return safe_substitute(r, **mappings)