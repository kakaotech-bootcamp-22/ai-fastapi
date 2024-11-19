import numpy as np
import torch

# 모델 입력 형식에 맞게 전처리, chunking 등의 전처리 수행 함수
def preprocess_input(input_data):
    """
    입력 데이터를 PyTorch Tensor로 변환.
    """
    input_array = np.array(input_data, dtype=np.float32)  # NumPy 배열로 변환
    return torch.tensor(input_array).unsqueeze(0)  # Batch 차원을 추가
