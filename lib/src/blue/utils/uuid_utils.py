import uuid

ID_SEPARATOR = ":"


def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]


def split_ids(canonical_id):
    return canonical_id.split(ID_SEPARATOR)


def extract_sid(canonical_id):
    return ID_SEPARATOR.join(extract_name_id(canonical_id))


def extract_name_id(canonical_id):
    return split_ids(canonical_id)[-2:]


def extract_prefix(canonical_id):
    splits = split_ids(canonical_id)
    if len(splits) > 2:
        return ID_SEPARATOR.join(splits[:-2])
    return None


def concat_ids(*ids):
    return ID_SEPARATOR.join(ids)
