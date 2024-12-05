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
            # spaced_text = self.kiwi.join(self.kiwi.analyze(text, normalize_coda=True)[0][0])  # 띄어쓰기 교정
            spaced_text = self.spacing(text)

            # 문장 분리
            result = ""
            for sentence in self.kiwi.split_into_sents(spaced_text):
                result += sentence.text.strip() + " [SEP]\n"  # 공백 제거 후 [SEP]\n 추가

            return result
        except Exception as e:
            logging.error(f"전처리 중 오류 발생: {str(e)}")
            return ""

# 텍스트를 256개 토큰 단위로 완전한 문장 단위로 나누는 함수 정의
def split_text_into_paragraphs(text, tokenizer, max_length=256):
    sentences = text.split("[SEP]\n")[:-1]  # 마지막 빈 요소 제거
    paragraphs = []
    paragraph_sentences = []  # 현재 문단에 포함될 문장들
    paragraph_length = 0  # 현재 문단의 토큰 개수

    for sentence in sentences:
        sentence_tokens = tokenizer.tokenize(sentence)
        sentence_length = len(sentence_tokens)  # 현재 문장의 토큰 개수

        # 현재 문장을 추가했을 때 max_length를 초과하면, 현재 문단을 완성하여 paragraphs에 추가
        if paragraph_length + sentence_length > max_length:
            paragraphs.append(" ".join(paragraph_sentences))
            paragraph_sentences = [sentence]  # 새로운 문단을 현재 문장으로 시작
            paragraph_length = sentence_length  # 새로운 문단의 토큰 길이 초기화
        else:
            # 현재 문장을 문단에 추가
            paragraph_sentences.append(sentence)
            paragraph_length += sentence_length + 1  # 문장 간의 공백을 고려해 +1 추가

    # 마지막 문단이 비어 있지 않으면 추가
    if paragraph_sentences:
        paragraphs.append(" ".join(paragraph_sentences))
    return paragraphs
