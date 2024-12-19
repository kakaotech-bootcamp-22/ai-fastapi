# POST 요청 전송
import os
from typing import Dict, Any
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

from aws_config import get_ssm_parameter
from utils.shared import tasks

# # .env 파일 로드
# load_dotenv()
#
# # 환경 변수에서 백엔드 URL 가져오기 (TEST, PROD 필요한 것으로 변경)
# BACKEND_URL = os.getenv("BACKEND_URL_PROD")

# 백엔드 서버 파라미터 경로
backend_url_param = "/config/ktb22/backend.server.url"

# # 테스트
# backend_url_param = "/config/ktb22/backend.test.url"

# 각 파라미터 값 가져오기
BACKEND_URL = get_ssm_parameter(backend_url_param)

# # 백엔드 로컬 테스트
# BACKEND_URL = "http://localhost:8001/review-check/response"

# POST 요청 전송 함수
def send_post_request(url: str, data: Dict[str, Any]) -> Dict:
    try:
        with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
            response = client.post(url, json=data)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {str(e)}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


# 작업 완료된 태스크를 처리하고 백엔드에 결과를 전송
def process_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task ID '{task_id}' not found")

    task = tasks[task_id]

    # print("Task data:", task)  # task 전체 출력
    if "result" not in task or task["result"] is None:
        raise ValueError(f"Task ID '{task_id}' has invalid or missing 'result' data")

    payload = task

    print('*** 2 : payload : ', payload, ' ***')

    try:
        # POST 요청 전송
        response = send_post_request(BACKEND_URL, payload)
        print(f"Backend response: {response}")

        return response

    except HTTPException as e:
        # 에러 발생 시 로깅 또는 상태 업데이트
        print(f"?? Error while sending result for Task ID '{task_id}': {e}")
        task["status"] = "ERROR"
        task["result"]["error"] = e.detail
