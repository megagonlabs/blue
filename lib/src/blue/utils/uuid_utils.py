import uuid

from blue.constant import Separator


def create_uuid():
    """Create a unique identifier.

    Returns:
        (str): Unique identifier string
    """
    return str(hex(uuid.uuid4().fields[0]))[2:]


def split_ids(canonical_id):
    """Split a canonical id into its components.

    Parameters:
        canonical_id (str): Canonical ID string

    Returns:
        (list[str]): List of ID components
    """
    return canonical_id.split(Separator.ID)


def extract_sid(canonical_id):
    """Extract the SID (short ID) from a canonical ID.

    Parameters:
        canonical_id (str): Canonical ID string

    Returns:
        (str): SID string
    """
    return Separator.ID.join(extract_name_id(canonical_id))


def extract_name_id(canonical_id):
    """Extract the name and ID from a canonical ID.

    Parameters:
        canonical_id (str): Canonical ID string

    Returns:
        ((str, str)): Tuple of (name, ID)
    """
    return split_ids(canonical_id)[-2:]


def extract_prefix(canonical_id):
    """Extract the prefix from a canonical ID.

    Parameters:
        canonical_id (str): Canonical ID string

    Returns:
        (str): Prefix string or None if not available
    """
    splits = split_ids(canonical_id)
    if len(splits) > 2:
        return Separator.ID.join(splits[:-2])
    return None


def concat_ids(*ids):
    """Concatenate multiple ID components.

    Parameters:
        *ids: ID components to concatenate

    Returns:
        (str): Concatenated ID string
    """
    return Separator.ID.join(ids)
