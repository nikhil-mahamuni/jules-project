def calculate_final_score(similarity: float, importance: float, confidence: float, recency: float, emotional_weight: float) -> float:
    """
    Ranking formula:
    final_score = similarity * 0.45
                + importance_score * 0.25
                + confidence_score * 0.15
                + recency_score * 0.10
                + emotional_weight * 0.05
    """
    return (
        similarity * 0.45 +
        importance * 0.25 +
        confidence * 0.15 +
        recency * 0.10 +
        emotional_weight * 0.05
    )
