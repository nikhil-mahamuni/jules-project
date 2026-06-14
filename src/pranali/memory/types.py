from enum import Enum

class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    GOAL = "goal"
    PROJECT = "project"
    RELATIONSHIP = "relationship"
    EMOTIONAL = "emotional"
    TASK = "task"
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    IDENTITY = "identity"

class MemorySource(str, Enum):
    CONVERSATION = "conversation"
    MANUAL = "manual"
    REFLECTION = "reflection"
    SYSTEM = "system"
    FUTURE_SENSOR = "future_sensor"
