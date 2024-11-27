import asyncio

from fastapi import APIRouter
from pydantic import BaseModel
import torch
from utils.load_model import load_model_and_tokenizer

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

router = APIRouter()

# 임시 저장소 (Redis 또는 DB로 대체 가능)
tasks = {}

# url: 네이버 블로그 링크
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드
chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 안 함 (Docker에서 메모리 문제 해결)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

class ReviewCheckRequest(BaseModel):
    requestId: str
    blogUrl: str

@router.post("/review_check")
async def submit_request(request: ReviewCheckRequest):
    # 작업 ID로 받은 requestID 사용
    task_id = request.requestId

    # 더미 데이터 초기화
    # task_id = "1"
    tasks[task_id] = {"status": "PENDING", "result": None}

    # 비동기 작업 처리 시뮬레이션
    await process_and_predict_from_url(task_id, request.blogUrl)

    return {
        "message": "Request received. Processing started.",
        "requestId": task_id
    }

from fastapi import HTTPException
from utils.crawling import crawl_url, parse_html
from utils.preprocess import TextProcessor, split_text_into_paragraphs


# 작업 처리 함수 : 비동기로 정의 (async)
# 비동기 함수 정의와 호출 위치 수정 + 기능 별 함수 분해
# 예측 함수
def predict_text(model, processed_text, tokenizer, max_len=64):
    """
    전처리된 텍스트를 입력으로 받아 모델이 분류 결과를 반환하도록 합니다.

    Args:
        model: 로드된 BERTClassifier 모델.
        processed_text (str): 전처리된 본문 텍스트.
        tokenizer: KoBERT 토크나이저.
        max_len (int): 최대 입력 길이.

    Returns:
        label (int): 분류 결과 (예: 0 또는 1).
        probabilities (list): 각 클래스에 대한 확률.
    """
    # 텍스트 토큰화 및 텐서 변환
    encoded_dict = tokenizer(
        processed_text,
        max_length=max_len,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )

    # 입력 데이터 생성
    input_ids = encoded_dict['input_ids']
    attention_mask = encoded_dict['attention_mask']
    token_type_ids = encoded_dict['token_type_ids']

    # 모델 입력
    with torch.no_grad():
        outputs = model(input_ids, attention_mask.sum(dim=1), token_type_ids)

    # 소프트맥스 확률 계산
    probabilities = torch.softmax(outputs, dim=1).cpu().numpy()[0]
    label = probabilities.argmax()  # 가장 높은 확률을 가진 클래스 선택

    return label, probabilities

'''
함수 호출은 작업이 완료될 때까지 기다림
작업이 진행되는 동안(url이 처리되는 동안), 다른 요청이나 작업 처리 가능
=> 서버가 동시에 여러 클라이언트의 요청을 효율적으로 처리 가능!
'''
async def process_and_predict_from_url(task_id: str, url: str):
    """
    사용자 입력 URL의 본문 데이터를 크롤링, 전처리하고 모델 예측 수행.

    Args:
        task_id (str): 작업 ID
        url (str): 크롤링할 URL

    Returns:
        None
    """
    try:
        tasks[task_id]["status"] = "IN_PROGRESS"

        # 1. 크롤링 수행
        soup = parse_html(driver, url)
        if soup is None:
            tasks[task_id]["status"] = "FAILED"
            tasks[task_id]["result"] = "HTML 파싱에 실패했습니다."
            return

        raw_text = crawl_url(soup)
        print('raw text:', raw_text)

        if not raw_text:
            tasks[task_id]["status"] = "FAILED"
            tasks[task_id]["result"] = "크롤링된 본문 데이터가 비어있습니다."
            return

        # 2. 전처리 수행
        processor = TextProcessor()
        processed_text = processor.process_text(raw_text)
        print("\n\n!!!!! processed_text:", processed_text)

        if not processed_text.strip():
            tasks[task_id]["status"] = "FAILED"
            tasks[task_id]["result"] = "전처리된 본문 데이터가 비어있습니다."
            return

        # 3. 텍스트를 문단으로 나누기
        model, tokenizer = load_model_and_tokenizer()
        print(f"\n\n Tokenizer 확인: {tokenizer}")

        paragraphs = split_text_into_paragraphs(processed_text, tokenizer)

        # 테스트용 출력
        print(f"\n\n @@@ 분리된 문단: {paragraphs}")

        # 3.  모델 로드 및 예측
        # 모델 평가 모드 전환
        model.eval()
        # (수정사항 2) paragraph에 저장된 요소들 각각에 대해서 predict_text 수행

        predicted_class, probability = predict_text(model, processed_text)


        # (수정사항 3) paragraph에 저장된 요소들 각각에 대한 predicted_class, probability를 활용해 soft_voting 수행

        # 작업 완료 상태 업데이트
        tasks[task_id]["status"] = "COMPLETED"
        tasks[task_id]["result"] = {
            "processed_text": processed_text,
            "prediction": predicted_class,
        }

    except Exception as e:
        tasks[task_id]["status"] = "FAILED"
        tasks[task_id]["result"] = str(e)


'''
실제 비동기로 작업 처리해주는 process_task 함수 부분
'''
# async def process_task(task_id: str, url: str):
#     # URL을 통한 전처리 및 모델 실행
#     try:
#         tasks[task_id]["status"] = "IN_PROGRESS"
#         await asyncio.sleep(3)  # 작업 처리 시간 시뮬레이션
#
#         # URL 기반 데이터 추출 및 모델로 처리 과정 (수정 예정)
#         # 더미 데이터
#         # tasks[task_id]["status"] = "COMPLETED"
#         # tasks[task_id]["result"] = {
#         #     "review_score": 30,
#         #     "summary_title": "판교역 돈까스 맛집 추천, 직장인들 점심 해결!",
#         #     "summary_content": "판교역 근처 돈까스 가게에 다녀왔어요. 고기는 부드럽고 튀김은 바삭하다! 맛있는 돈까스 찾는 분들께 강추 !",
#         #     "reason": "블로그 글 하단에 광고 배너가 있어요."
#         # }
#
#         # 상태 완료로 변경
#         tasks[task_id]["status"] = "COMPLETED"
#
#     except Exception as e:
#         tasks[task_id]["status"] = "FAILED"
#         tasks[task_id]["result"] = str(e)

@router.get("/result/{task_id}")
async def get_result(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task ID '{task_id}' not found")

    task = tasks[task_id]
    if task["status"] == "COMPLETED":
        return {
            "status": "COMPLETED",
            "review_score": task["result"]["review_score"],
            "summary_title": task["result"]["summary_title"],
            "summary_content": task["result"]["summary_content"],
            "reason": task["result"]["reason"]
        }

    elif task["status"] == "PENDING" or task["status"] == "IN_PROGRESS":
        return {"status": "IN_PROGRESS", "message": "Result is not ready yet"}
    else:
        return {"status": "FAILED", "message": "Task processing failed"}

if __name__ == "__main__":
    # 테스트용 task_id와 url
    task_id = "123e4567-e89b-12d3-a456-426614174000"
    url = "https://blog.naver.com/tkdtkdgns1/223604228666"

    # tasks 초기화
    tasks[task_id] = {"status": "PENDING", "result": None}

    # asyncio.run으로 비동기 함수 실행
    asyncio.run(process_and_predict_from_url(task_id, url))

    # 결과 확인
    print(tasks[task_id])

'''
더미 데이터로 돌아가는 process_task 함수 코드
'''
# def process_task(task_id: str):
#     # URL을 통한 전처리 및 모델 실행
#     try:
#         # tasks[task_id]["status"] = "IN_PROGRESS"
#         # await asyncio.sleep(3)  # 작업 처리 시간 시뮬레이션
#
#         # URL 기반 데이터 추출 및 모델로 처리 과정 (수정 예정)
#         # 더미 데이터
#         tasks[task_id]["status"] = "COMPLETED"
#         tasks[task_id]["result"] = {
#             "review_score": 30,
#             "summary_title": "판교역 돈까스 맛집 추천, 직장인들 점심 해결!",
#             "summary_content": "판교역 근처 돈까스 가게에 다녀왔어요. 고기는 부드럽고 튀김은 바삭하다! 맛있는 돈까스 찾는 분들께 강추 !",
#             "reason": "블로그 글 하단에 광고 배너가 있어요."
#         }
#
#         # # 상태 완료로 변경
#         # tasks[task_id]["status"] = "COMPLETED"
#
#     except Exception as e:
#         tasks[task_id]["status"] = "FAILED"
#         tasks[task_id]["result"] = str(e)