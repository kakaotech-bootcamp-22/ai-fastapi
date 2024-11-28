import torch
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

    # def gen_attention_mask(self, token_ids, valid_length):
    #     attention_mask = torch.zeros_like(token_ids)
    #     for i, v in enumerate(valid_length):
    #         attention_mask[i][:v] = 1
    #     return attention_mask

    def gen_attention_mask(self, token_ids, valid_length):
        # valid_length가 텐서인 경우 정수로 변환
        if isinstance(valid_length, torch.Tensor):
            valid_length = valid_length.cpu().tolist()  # 텐서를 리스트로 변환

        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:int(v)] = 1  # 정수로 변환 후 사용
        return attention_mask

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)

        # BertModel의 출력
        bert_output = self.bert(
            input_ids=token_ids,
            token_type_ids=segment_ids.long(),
            attention_mask=attention_mask.float().to(token_ids.device)
        )

        # bert_output의 두 번째 출력값인 pooler_output을 사용
        pooler_output = bert_output[1]

        if self.dr_rate:
            out = self.dropout(pooler_output)
        else:
            out = pooler_output

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
    '''
    torch.load 함수는 기본적으로 모델 가중치만 로드하려고 시도한다
    weights_only=True -> 체크포인트 파일이 단순히 모델 가중치만 포함한다면, weights_only=True를 사용할 수 있다
    (그게 보안면에서 더 안전함)
    
    지금 파일은 가중치만 포함하고 있는 파일이 아니라서
    '''
    checkpoint = torch.load(checkpoint_path, map_location=device)  # weights_only=True -> 체크포인트 파일이 단순히 모델 가중치만 포함한다면, weights_only=True를 사용할 수 있다

    # 모델 상태 복원 : 로드된 체크포인트에서 해당 모델의 가중치와 상태 복원
    model.load_state_dict(checkpoint['model_state_dict'])

    print(f"모델 로드 완료: {checkpoint_path}")
    print(f"에포크: {checkpoint['epochs']}, 검증 정확도: {checkpoint['val_acc']}")

    return model


# if __name__ == "__main__":
#     model, tokenizer = load_model_and_tokenizer()
#
#     print(model, tokenizer)



# # 로드 함수 예시
# def load_model():
#     # 사용할 최종 모델 .tar 파일명 수정하는 부분
#     checkpoint_path = os.path.join(os.getcwd(), "models/checkpoint_epoch_36.tar")
#
#     bert = BertModel.from_pretrained("skt/kobert-base-v1")  # BERT 모델 로드
#     model = load_model_from_checkpoint(checkpoint_path, lambda dr_rate: BERTClassifier(bert, dr_rate=dr_rate))
#     return model


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