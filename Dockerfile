FROM python:3.11-slim 

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 도구 설치
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 로컬 코드 복사
COPY . .

# S3에서 다운로드한 파일 복사 (Jenkins가 처리한 파일 포함)
COPY *.pt /app/models/
COPY pykospacing/ /app/pykospacing/

# 라이브러리 설치
RUN pip install --no-cache-dir --no-deps -r requirements.txt

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install -e /app/pykospacing/

# RUN pip install git+https://github.com/SKTBrain/KoBERT.git@5c46b1c68e4755b54879431bd302db621f4d2f47
# RUN pip install git+https://github.com/SKTBrain/KoBERT.git@5c46b1c68e4755b54879431bd302db621f4d2f47#subdirectory=kobert_hf

# 파일 압축 해제
# RUN tar -xvf /app/models/checkpoint_epoch_36.tar -C /app/models && rm /app/models/checkpoint_epoch_36.tar

# FastAPI 실행 포트 설정
EXPOSE 8000

# FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
