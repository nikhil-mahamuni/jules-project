from src.pranali.memory.scorer import calculate_final_score

def test_calculate_final_score():
    score = calculate_final_score(
        similarity=0.8,
        importance=0.6,
        confidence=0.9,
        recency=1.0,
        emotional_weight=0.2
    )
    # 0.8*0.45 + 0.6*0.25 + 0.9*0.15 + 1.0*0.10 + 0.2*0.05
    # 0.36 + 0.15 + 0.135 + 0.1 + 0.01 = 0.755
    assert abs(score - 0.755) < 0.001
