import uuid

def generate_uuid() -> uuid.UUID:
    """Generate a new UUID4."""
    return uuid.uuid4()

def generate_uuid_str() -> str:
    """Generate a new UUID4 as a string."""
    return str(uuid.uuid4())
