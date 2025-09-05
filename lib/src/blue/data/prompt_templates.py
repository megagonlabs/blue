AGGREGATION_PROMPT = """
The data structure is 'source' -> 'database' -> 'collection' -> 'entity'
You are given the text descriptions from all '{child_type}' that belongs to a ' {parent_type}'.
Please generate a text description for the {parent_type} based on the text descriptions of the {child_type}.
Here are the requirements:
- The description should be concise and informative.
- The description should be a single sentence.
- The description should be able to be used to distinguish the {parent_type} from other {parent_type}s. Include necessary concise summary if the description is too vague.
- Please only return the description, don't include any other explanation in the output.

'{child_type}' descriptions:
{child_descriptions}

Metadata for the parent '{parent_type}':
{parent_metadata}

Output (single sentence only):
"""