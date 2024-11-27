import logging
from kiwipiepy import Kiwi
from pykospacing import Spacing

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TextProcessor:
    def __init__(self):
        """
        전처리를 위한 Kiwi와 PyKoSpacing 초기화
        """
        self.kiwi = Kiwi(num_workers=2)
        self.spacing = Spacing()

    def process_text(self, text: str) -> str:
        """
        단일 텍스트를 전처리합니다.
        1. 띄어쓰기 교정
        2. 문장 분리
        3. [SEP]\n으로 문장 연결

        Args:
            text (str): 전처리할 원본 텍스트

        Returns:
            str: 전처리된 텍스트
        """
        if not isinstance(text, str) or not text.strip():
            logging.warning("입력 텍스트가 비어있거나 유효하지 않습니다.")
            return ""

        try:
            # 띄어쓰기 교정
            spaced_text = self.spacing(text)

            # 문장 분리
            result = ""
            for sentence in self.kiwi.split_into_sents(spaced_text):
                result += sentence.text.strip() + " [SEP]\n"  # 공백 제거 후 [SEP]\n 추가

            return result
        except Exception as e:
            logging.error(f"전처리 중 오류 발생: {str(e)}")
            return ""




# def preprocess_input(tokenizer, input_text, max_len=256):
#     """
#     입력 텍스트를 모델이 처리할 수 있는 형식으로 변환합니다.
#     Args:
#         tokenizer: KoBERT Tokenizer.
#         input_text (str): 사용자 입력 텍스트.
#         max_len (int): 최대 시퀀스 길이.
#     Returns:
#         dict: 토큰화된 텐서 데이터.
#     """
#     encoded_input = tokenizer(
#         input_text,
#         return_tensors="pt",
#         padding="max_length",
#         truncation=True,
#         max_length=max_len
#     )
#     return encoded_input




# import numpy as np
# import torch
#
# # 모델 입력 형식에 맞게 전처리, chunking 등의 전처리 수행 함수
# def preprocess_input(input_data):
#     """
#     입력 데이터를 PyTorch Tensor로 변환.
#     """
#     input_array = np.array(input_data, dtype=np.float32)  # NumPy 배열로 변환
#     return torch.tensor(input_array).unsqueeze(0)  # Batch 차원을 추가
