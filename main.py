from fastapi import FastAPI
from routers import review_check  # 라우터 임포트
from utils.task_logic import process_task

# FastAPI 인스턴스 생성
app = FastAPI()

# 라우터 등록
app.include_router(review_check.router, prefix="/review-check", tags=["Prediction"])  # tags=["Prediction"] : OpenAPI 문서화 및 API 탐색을 용이하게 하기 위한 메타데이터, 없어도 되는 인자이긴 함

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/review-check/response")
async def receive_response():
    from utils.shared import tasks

    # 초기화된 더미 데이터
    tasks["123e4567-e89b-12d3-a456-426614174000"] = {
        "status": "COMPLETED",
        "result": {
            "blogUrl": "https://blog.naver.com/tkdtkdgns1/223604228666",
            "summaryText": "This post appears genuine.",
            "review_score": 85,
            "reason": "Minimal promotional language found."
        }
    }

    # 비동기 처리 함수 호출
    result = await process_task(task_id="123e4567-e89b-12d3-a456-426614174000")

    return result




'''
main에서 from routers import review_check
review_check.py에서 from utils.prediction_logic import process_and_predict_from_url 
prediction 
'''