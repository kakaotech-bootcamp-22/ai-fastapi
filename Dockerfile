# Stage 1: Build Stage
FROM python:3.11-slim AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 로컬 코드 복사
COPY . .

# S3에서 다운로드한 파일 복사 (Jenkins가 처리한 파일 포함)
COPY *.tar /app/models/
COPY pykospacing/ /app/pykospacing/

# 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 파일 압축 해제
# RUN tar -xvf /app/models/checkpoint_epoch_36.tar -C /app/models && rm /app/models/checkpoint_epoch_36.tar

# Stage 2: Runtime Stage
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 빌드된 코드 및 파일만 복사
COPY --from=builder /app /app

# FastAPI 실행 포트 설정
EXPOSE 8000

# FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
