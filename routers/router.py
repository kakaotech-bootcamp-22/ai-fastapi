from fastapi import APIRouter

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from schemas.review_check import ReviewCheckRequest
from utils.prediction_logic import process_and_predict_from_url

from utils.shared import tasks

import asyncio

router = APIRouter()

# Selenium WebDriver 설정
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# chrome_options = Options()
# chrome_options.add_argument("--headless")  # 헤드리스 모드
# chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
# chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 안 함 (Docker에서 메모리 문제 해결)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

@router.post("/")
async def process_review_request(request: ReviewCheckRequest):
    # 작업 ID로 받은 requestID 사용
    task_id = request.requestId
    tasks[task_id] = {"status": "PENDING", "result": None}

    # 비동기 작업 처리 시뮬레이션
    asyncio.create_task(process_and_predict_from_url(task_id, request.blogUrl, driver))

    return {"message": "Request received. Processing started.", "requestId": task_id}


if __name__ == "__main__":
    # 더미 데이터 생성
    task_id = "123e4567-e89b-12d3-a456-426614174000"