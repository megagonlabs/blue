import json
import logging
import uuid
import re


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
