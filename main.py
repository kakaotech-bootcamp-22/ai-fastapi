from fastapi import FastAPI
from routers import router  # 라우터 임포트
from utils.task_logic import process_task
from utils.shared import tasks

# FastAPI 인스턴스 생성
app = FastAPI()

# 라우터 등록 : 앞 쪽 router가 파일명
app.include_router(router.router, prefix="/review-check", tags=["Prediction"])  # tags=["Prediction"] : OpenAPI 문서화 및 API 탐색을 용이하게 하기 위한 메타데이터, 없어도 되는 인자이긴 함

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# ai -> backend 테스트 하기 위한 api (테스트가 가능한거?)
@app.post("/review-check/response")
async def receive_response():

    result = '!!!! got response !!!!!'

    return result
