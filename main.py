from fastapi import FastAPI
from routers import prediction  # 라우터 임포트

# FastAPI 인스턴스 생성
app = FastAPI()

# 라우터 등록
app.include_router(prediction.router, prefix="/api", tags=["Prediction"])  # tags=["Prediction"] : OpenAPI 문서화 및 API 탐색을 용이하게 하기 위한 메타데이터, 없어도 되는 인자이긴 함

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
