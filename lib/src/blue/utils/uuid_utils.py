import uuid

from blue.core import Separator


def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]


def split_ids(canonical_id):
    return canonical_id.split(Separator.ID)


def extract_sid(canonical_id):
    return Separator.ID.join(extract_name_id(canonical_id))


def extract_name_id(canonical_id):
    return split_ids(canonical_id)[-2:]


def extract_prefix(canonical_id):
    splits = split_ids(canonical_id)
    if len(splits) > 2:
        return Separator.ID.join(splits[:-2])
    return None


def concat_ids(*ids):
    return Separator.ID.join(ids)
