import torch
from transformers import BertModel
import torch.nn as nn

# 모델 클래스 정의
# 리팩토링 필요
class BERTClassifier(nn.Module):
    def __init__(self, bert, hidden_size=768, num_classes=2, dr_rate=None, params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate
        self.classifier = nn.Linear(hidden_size, num_classes) # classification 을 위한 레이어
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)

        # 디버깅 코드 추가: 입력값과 임베딩 출력값의 모양 확인
        # print(f"token_ids shape: {token_ids.shape}")
        # print(f"segment_ids shape: {segment_ids.shape}")
        # print(f"attention_mask shape: {attention_mask.shape}")

        _, pooler = self.bert(
            input_ids=token_ids,
            token_type_ids=segment_ids.long(),
            attention_mask=attention_mask.float().to(token_ids.device)
        )

        # BERT 출력값의 모양 확인
        # print(f"BERT output shape: {_.shape}")
        # print(f"BERT pooler shape: {pooler.shape}")

        if self.dr_rate:
            out = self.dropout(pooler)
        else:
            out = pooler

        return self.classifier(out)

def load_model_from_checkpoint(checkpoint_path, bert_model_class):
    """
    .tar 파일에서 모델 가중치를 로드하고 평가 모드로 설정합니다.
    Args:
        checkpoint_path (str): .tar 파일 경로.
        bert_model_class: BERT 모델 클래스.
    Returns:
        model: PyTorch 모델 (BERTClassifier).
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 모델 초기화
    model = bert_model_class(dr_rate=0.5).to(device)

    # 체크포인트 로드
    checkpoint = torch.load(checkpoint_path, map_location=device)

    # 모델 상태 복원 : 로드된 체크포인트에서 해당 모델의 가중치와 상태 복원
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    print(f"모델 로드 완료: {checkpoint_path}")
    print(f"에포크: {checkpoint['epoch']}, 검증 정확도: {checkpoint['val_acc']}")

    return model

# 로드 함수 예시
def load_model():
    # 사용할 최종 모델 .tar 파일명 수정하는 부분
    checkpoint_path = "models/checkpoint_epoch_36.tar"  # .tar 파일 경로
    bert = BertModel.from_pretrained("skt/kobert-base-v1")  # BERT 모델 로드
    model = load_model_from_checkpoint(checkpoint_path, lambda dr_rate: BERTClassifier(bert, dr_rate=dr_rate))
    return model


# import os
# import torch
#
# # 모델 불러오는 함수
# def load_model():
#     """
#     로컬 모델을 PyTorch로 로드.
#     """
#     # 절대 경로 생성
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     model_path = os.path.join(base_dir, "../models/my_model.pt")
#     model = torch.load(model_path, map_location=torch.device("cpu"))
#
#     model.eval()  # 평가 모드 설정
#
#     return model