import json
import uuid
import re


def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]


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
