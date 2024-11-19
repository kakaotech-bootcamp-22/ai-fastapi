import os
import torch

# 모델 불러오는 함수
def load_model():
    """
    로컬 모델을 PyTorch로 로드.
    """
    # 절대 경로 생성
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "../models/my_model.pt")
    model = torch.load(model_path, map_location=torch.device("cpu"))

    model.eval()  # 평가 모드 설정

    return model