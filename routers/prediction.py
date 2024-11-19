from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import asyncio

router = APIRouter()

# 딥러닝 모델 로드 - process_task 함수에서 활용 예정
# model = load_model()

# 임시 저장소 (Redis 또는 DB로 대체 가능)
tasks = {}

class URLRequest(BaseModel):
    URL: str

@router.post("/submit")
async def submit_request(request: URLRequest):
    # 작업 ID 생성
    # task_id = str(uuid.uuid4())
    task_id = "1"
    tasks[task_id] = {"status": "PENDING", "result": None}

    # 비동기 작업 처리 시뮬레이션
    process_task(task_id)

    return {"task_id": task_id, "message": "Request received", "estimated_time": "60 seconds"}

def process_task(task_id: str):
    # URL을 통한 전처리 및 모델 실행
    try:
        # tasks[task_id]["status"] = "IN_PROGRESS"
        # await asyncio.sleep(3)  # 작업 처리 시간 시뮬레이션

        # URL 기반 데이터 추출 및 모델로 처리 과정 (수정 예정)
        # 더미 데이터
        tasks[task_id]["status"] = "COMPLETED"
        tasks[task_id]["result"] = {
            "review_score": 30,
            "summary_title": "판교역 돈까스 맛집 추천, 직장인들 점심 해결!",
            "summary_content": "판교역 근처 돈까스 가게에 다녀왔어요. 고기는 부드럽고 튀김은 바삭하다! 맛있는 돈까스 찾는 분들께 강추 !",
            "reason": "블로그 글 하단에 광고 배너가 있어요."
        }

        # # 상태 완료로 변경
        # tasks[task_id]["status"] = "COMPLETED"

    except Exception as e:
        tasks[task_id]["status"] = "FAILED"
        tasks[task_id]["result"] = str(e)


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