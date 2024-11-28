import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from utils.prediction_logic import process_and_predict_from_url
from fastapi import HTTPException

from utils.shared import tasks

router = APIRouter()
# 
# # 임시 저장소 (Redis 또는 DB로 대체 가능)
# tasks = {}

# Selenium WebDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드
chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 안 함 (Docker에서 메모리 문제 해결)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

class ReviewCheckRequest(BaseModel):
    requestId: str
    blogUrl: str

@router.post("/")
async def submit_request(request: ReviewCheckRequest):
    # 작업 ID로 받은 requestID 사용
    task_id = request.requestId
    tasks[task_id] = {"status": "PENDING", "result": None}

    # 비동기 작업 처리 시뮬레이션
    await process_and_predict_from_url(task_id, request.blogUrl, driver)

    return {"message": "Request received. Processing started.", "requestId": task_id}

@router.post("/result")
async def send_completed_results():
    for task_id, task in tasks.items():
        if task["status"] == "COMPLETED":
            backend_url = "https://your-backend-url.com/api/receive-result"  # URL 수정

            # payload 아직 미완
            payload = {
                "requestId": task_id,
                "blogUrl": task["result"].get("blogUrl", "Unknown"),
                "summaryTitle": "Analysis Complete",
                "summaryText": task["result"].get("summaryText", "Analysis completed successfully."),
                "score": task["result"].get("review_score", 0),
                "evidence": task["result"].get("reason", "No evidence found.")
            }

            try:
                # Send the POST request to the backend
                import requests
                response = requests.post(backend_url, json=payload)

                # Check if the request was successful
                if response.status_code == 200:
                    # Mark the task as sent to avoid duplicate sending
                    task["status"] = "SENT"
                    print(f"Task {task_id} sent successfully.")
                elif response.status_code == 400:
                    print(f"Task {task_id} failed: 400 Bad Request - Missing required data. Response: {response.text}")

                elif response.status_code == 404:
                    print(f"Task {task_id} failed: 404 Not Found - Request ID not found on the backend.")

                elif response.status_code == 409:
                    print(f"Task {task_id} failed: 409 Conflict - Result already processed on the backend.")

                elif response.status_code == 500:
                    print(f"Task {task_id} failed: 500 Internal Server Error. Response: {response.text}")

                else:
                    print(f"Task {task_id} failed with unexpected status code {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"Error sending task {task_id}: {str(e)}")

    return {"message": "Processed all completed tasks."}


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