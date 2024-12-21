from fastapi import APIRouter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from schemas.review_check import ReviewCheckRequest
from utils.prediction_logic import process_and_predict_from_url
from utils.shared import tasks


router = APIRouter()

# Selenium WebDriver 설정
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--remote-debugging-port=9222')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--proxy-server="direct://"')
chrome_options.add_argument('--proxy-bypass-list=*')
chrome_options.add_argument('--start-maximized')

# 타임아웃 설정 추가
chrome_options.page_load_strategy = 'normal'

# ChromeDriverManager 대신 시스템에 설치된 ChromeDriver 사용
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(
    service=service,
    options=chrome_options
)

# 전역 타임아웃 설정
driver.set_page_load_timeout(30)
driver.implicitly_wait(10)

@router.post("")
def process_review_request(request: ReviewCheckRequest):
    # 작업 ID로 받은 requestID 사용
    task_id = request.requestId
    tasks[task_id] = {"status": "PENDING", "result": None}

    process_and_predict_from_url(task_id, request.blogUrl, driver)

    return {"message": "Request received. Processing started.", "requestId": task_id}


if __name__ == "__main__":
    # 더미 데이터 생성
    task_id = "123e4567-e89b-12d3-a456-426614174000"
