from fastapi import FastAPI
from routers import prediction  # 라우터 임포트

# FastAPI 인스턴스 생성
app = FastAPI()

# 라우터 등록
app.include_router(prediction.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
