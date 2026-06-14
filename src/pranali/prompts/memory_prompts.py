def build_memory_extraction_prompt(user_display_name: str, recent_turns: str) -> str:
    return f"""You are an expert memory extractor. Extract meaningful long-term memories from the recent conversation context.

User's preferred name: {user_display_name}

Recent Conversation:
{recent_turns}

Extract memories as a strict JSON array of objects. Do NOT extract every detail, only extract important things like facts, preferences, goals, projects, relationships, emotional signals, identity instructions, and task commitments.
Do not store API keys, passwords, secrets, tokens, or private credentials.

Return ONLY valid JSON matching this schema:
[
  {{
    "memory_type": "fact|preference|goal|project|relationship|emotional|task|semantic|episodic|identity",
    "title": "Short descriptive title",
    "content": "Detailed memory content",
    "summary": "Brief summary",
    "entities": ["entity1", "entity2"],
    "tags": ["tag1", "tag2"],
    "importance_score": 0.0 to 1.0 (float),
    "confidence_score": 0.0 to 1.0 (float),
    "emotional_weight": 0.0 to 1.0 (float),
    "sensitive": boolean (true if contains PII or sensitive info, but remember NO PASSWORDS),
    "confirmed": boolean (true if explicitly confirmed by user)
  }}
]

If there are no new memories to extract, return an empty array: []
"""
