# 모델 결과 값을 soft voting 하는 함수

def soft_voting(paragraph_probabilities):
    total_real_prob = sum(p[0] for p in paragraph_probabilities)
    total_fake_prob = sum(p[1] for p in paragraph_probabilities)
    num_paragraphs = len(paragraph_probabilities)

    # 문단 수가 0인 경우 처리
    if num_paragraphs == 0:
        return {"real_probability": 0.0, "fake_probability": 0.0}

    final_real_prob = total_real_prob / num_paragraphs
    final_fake_prob = total_fake_prob / num_paragraphs

    return {
        "real_probability": final_real_prob,
        "fake_probability": final_fake_prob
    }
