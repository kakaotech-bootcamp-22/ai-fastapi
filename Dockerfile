# Stage 1: Build Stage
FROM python:3.11-slim AS builder
WORKDIR /app

# requirements.txt만 먼저 복사해서 캐시 활용
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 파일들 복사
COPY . .
COPY *.tar /app/models/
COPY pykospacing/ /app/pykospacing/

# Stage 2: Runtime Stage
FROM python:3.11-slim
WORKDIR /app

# 필요한 파일들만 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /app/models/ /app/models/
COPY --from=builder /app/pykospacing/ /app/pykospacing/
COPY --from=builder /app/main.py /app/

# FastAPI 실행 포트 설정  
EXPOSE 8000

# FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
