import torch
import os
from transformers import BertModel
from kobert_tokenizer import KoBERTTokenizer
from utils.load_model import load_model_from_checkpoint, BERTClassifier

def predict_text(model, processed_text, tokenizer, max_len=64):
    encoded_dict = tokenizer(
        [processed_text],
        max_length=max_len,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )

    input_ids = encoded_dict['input_ids']
    attention_mask = encoded_dict['attention_mask']

    # valid_length 계산 (attention_mask의 합)
    valid_length = attention_mask.sum(dim=1)

    # segment_ids (token_type_ids) 생성 (모두 0으로)
    segment_ids = torch.zeros_like(input_ids)

    # 모델 입력
    with torch.no_grad():
        outputs = model(
            token_ids=input_ids,
            valid_length=valid_length,
            segment_ids=segment_ids
        )

    probabilities = torch.softmax(outputs, dim=1).cpu().numpy()

    real_prob = probabilities[0][0]
    fake_prob = probabilities[0][1]

    return real_prob, fake_prob

def load_model_and_tokenizer():
    # 모델 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 상위 디렉토리로 이동
    checkpoint_path = os.path.join(base_dir, "models", "checkpoint_epoch_6.pt")

    bert = BertModel.from_pretrained("skt/kobert-base-v1")  # BERT 모델 로드
    model = load_model_from_checkpoint(checkpoint_path, lambda dr_rate: BERTClassifier(bert, dr_rate=dr_rate))
    tokenizer = KoBERTTokenizer.from_pretrained("skt/kobert-base-v1")  # KoBERT 토크나이저 로드

    return model, tokenizer