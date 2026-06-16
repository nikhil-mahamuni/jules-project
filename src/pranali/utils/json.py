import json
from typing import Any

def to_json(obj: Any) -> str:
    """Convert an object to a JSON string."""
    return json.dumps(obj, default=str)

def from_json(json_str: str) -> Any:
    """Convert a JSON string to an object."""
    return json.loads(json_str)
