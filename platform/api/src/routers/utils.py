def is_alphanumeric_underscore(input_string):
    """
    Checks if the string contains only alpha-numeric characters and underscores.
    """
    if not input_string:  # optional: handle empty strings
        return False
    return all(c.isalnum() or c == '_' for c in input_string)
