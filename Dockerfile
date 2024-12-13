FROM python:3.11-slim 



# 필요한 도구 설치
RUN apt-get update && apt-get install -y \ 
    git \
    wget \
    gnupg \
    unzip \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
&& rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_131.0.6778.139-1_amd64.deb \
    && apt-get update \
    && apt install -y ./google-chrome-stable_131.0.6778.139-1_amd64.deb \
    && rm google-chrome-stable_131.0.6778.139-1_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver 설치 (특정 버전 사용)
RUN wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/131.0.6778.108/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/ \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64


# 작업 디렉토리 설정
WORKDIR /app
# ENV PYTHONPATH=/app
# 로컬 코드 복사
COPY . .

# S3에서 다운로드한 파일 복사 (Jenkins가 처리한 파일 포함)
COPY *.pt /app/models/
COPY pykospacing/ /app/pykospacing/

# 라이브러리 설치
RUN pip install --no-cache-dir --no-deps -r requirements.txt

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install -e /app/pykospacing/


RUN chmod +x /usr/local/bin/chromedriver

# Chrome 샌드박스 비활성화를 위한 디렉토리 생성
RUN mkdir -p /var/run/chrome && chmod -R 777 /var/run/chrome

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# 파일 압축 해제
# RUN tar -xvf /app/models/checkpoint_epoch_36.tar -C /app/models && rm /app/models/checkpoint_epoch_36.tar

# FastAPI 실행 포트 설정
EXPOSE 8000

# FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
