import json
import logging
import uuid
import re
import string

def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]


def extract_json(text):
    """
    Helper function to deal with markdown returned by extractor
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Regular expression pattern to match JSON-like structures
        json_pattern = r"```json\s*({.*?})\s*```"

        # Find all matches in the markdown text
        matches = re.findall(json_pattern, text, re.DOTALL)
        if len(matches) > 1:
            logging.warning(
                "More than one JSON object returned. loading only the first one"
            )
        # Parse the matches as JSON
        try:
            json_object = json.loads(matches[0])
            return json_object
        except json.JSONDecodeError:
            logging.warning("Invalid JSON object found, skipping...")
            return {}


def remove_non_alphanumeric(input_string):
    # Use regex to remove all non-alphanumeric characters
    cleaned_string = re.sub(r"[^a-zA-Z0-9 ]", "", input_string)
    cleaned_string = cleaned_string.replace(" ", "_")
    return cleaned_string


def parse_result(result):
    columns = result["result"]["columns"]
    data = result["result"]["data"]
    job_list = []
    for item in data:
        job = {key: value for key, value in zip(columns, item)}
        job_list.append(job)
    return {"Jobs": job_list}

def camel_case(string):
    words = string.split("_")
    return " ".join(word.capitalize() for word in words)

