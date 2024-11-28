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
    print(f"Softmax probabilities: {probabilities}")

    real_prob = probabilities[0][0]
    fake_prob = probabilities[0][1]
    print(real_prob, fake_prob)

    return real_prob, fake_prob




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

        # 각 문단의 확률값 저장
        paragraph_probabilities = []

        print('문단 개수 : ', len(paragraphs))

        for paragraph in paragraphs:
            real_prob, fake_prob = predict_text(model, paragraph, tokenizer)
            paragraph_probabilities.append([real_prob, fake_prob])
            print(f"Paragraph: {paragraph}")

        # 각 문단별 확률 확인
        print(f"Paragraph probabilities: {paragraph_probabilities}")

        # (수정사항 3) paragraph에 저장된 요소들 각각에 대한 predicted_class, probability를 활용해 soft_voting 수행

        # 작업 완료 상태 업데이트
        tasks[task_id]["status"] = "COMPLETED"
        # tasks[task_id]["result"] = {
        #     "processed_text": processed_text,
        #     "prediction": predicted_class,
        # }

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

    # # 테스트용 task_id와 url
    # task_id = "123e4567-e89b-12d3-a456-426614174000"
    # url = "https://blog.naver.com/tkdtkdgns1/223604228666"
    #
    # # tasks 초기화
    # tasks[task_id] = {"status": "PENDING", "result": None}
    #
    # # # asyncio.run으로 비동기 함수 실행
    # # asyncio.run(process_and_predict_from_url(task_id, url))
    #
    # model, tokenizer = load_model_and_tokenizer()
    # processed_text = "판교 맛집 중국집 가족 모임 룸 식당 판교 맛집 중국집 가족 모임 룸 식당 팔복 판교 안녕하세요 오늘은 아주 오랜만에 판교 맛집을 여러분들에게 소개해 드리도록 하겠습니다.  이번에 새로 오픈한 신상 판교 맛집 소식을 듣고 저도 어제 휴일을 맞이하여 배우자와 함께 다녀 왔는데 정말 맛있는 중식당 중국집이었습니다.  개별 프라이빗 룸 마련이 잘 되어 있어서 프라이빗 한  식사를 할 수 있어서 좋았고 무엇보다 정말 너무나도 맛있는 요리들을 맛볼 수 있어서 정말 행복했던 판교 맛집 팔복 판교입니다.  주차도 편하게 가능했고 정말 처음 보는 비주얼의 눈도 호강하고 입도 호강하고 온 여태까지 가봤던 중국집 중 손에 꼽는 중국집인데요!  요즘 흑백 요리사에서 중화요리 많이 봤었어서 먹고 싶어서 다녀왔는데 정말 너무나도 만족하고 다 녀왔던 팔 복 판교 솔직 후기 네이버 블로그 포스팅 지금 바로 시작해 보도록 하겠습니다!! "
    #
    # predict_text(model, processed_text, tokenizer, max_len=64)
    #
    #
    # # 결과 확인
    # print(tasks[task_id])

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