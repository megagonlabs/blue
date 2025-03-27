import uuid

def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]