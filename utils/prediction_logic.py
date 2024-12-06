import asyncio
from ssl import Options

from selenium.webdriver.chrome import webdriver

from utils.summarize import generate_summary
from utils.task_logic import process_task
from utils.shared import tasks
from utils.crawling import parse_html, crawl_url
from utils.model_utils import load_model_and_tokenizer, predict_text
from utils.preprocess import TextProcessor, split_text_into_paragraphs
from utils.soft_voting import soft_voting

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# 비동기 작업 처리 함수 : 전처리부터 soft-voting까지
'''
함수 호출은 작업이 완료될 때까지 기다림
작업이 진행되는 동안(url이 처리되는 동안), 다른 요청이나 작업 처리 가능
=> 서버가 동시에 여러 클라이언트의 요청을 효율적으로 처리 가능!
'''
async def process_and_predict_from_url(task_id: str, url: str, driver):
    """
    사용자 입력 URL의 본문 데이터를 크롤링, 전처리하고 모델 예측 수행.

    Args:
        task_id (str): 작업 ID
        url (str): 크롤링할 URL

    Returns:
        None
    """
    try:
        tasks[task_id]["status"] = "IN_PROGRESS"

        # 1. 크롤링 수행
        soup = parse_html(driver, url)
        if soup is None:
            tasks[task_id]["status"] = "FAILED"
            tasks[task_id]["result"] = "HTML 파싱에 실패했습니다."
            return

        raw_text = crawl_url(soup)
        # print('*** raw text:', raw_text)

        if not raw_text:
            tasks[task_id]["status"] = "FAILED"
            tasks[task_id]["result"] = "크롤링된 본문 데이터가 비어있습니다."
            return

        # 2. 전처리 수행
        processor = TextProcessor()
        processed_text = processor.process_text(raw_text)

        # print("\n\n*** processed_text:", processed_text)

        # 2-1. 전처리 된 텍스트 요약하기
        parsed_result = generate_summary(processed_text)
        print('*** Print parsedResult in Prediction_logic', parsed_result)

        title_summary = parsed_result["Title"]
        content_summary = parsed_result["Summary"]

        print('TITLE SUMMARY : ', title_summary,'\n\n', 'CONTENT SUMMARY: ', content_summary)

        if not processed_text.strip():
            tasks[task_id]["status"] = "FAILED"
            tasks[task_id]["result"] = "전처리된 본문 데이터가 비어있습니다."
            return

        # 3. 텍스트를 문단으로 나누기
        model, tokenizer = load_model_and_tokenizer()
        # print(f"\n\n Tokenizer 확인: {tokenizer}")

        paragraphs = split_text_into_paragraphs(processed_text, tokenizer)

        # 테스트용 출력
        # print(f"\n\n @@@ 분리된 문단: {paragraphs}")

        # 4. 모델 로드 및 예측
        model.eval()    # 모델 평가 모드 전환

        # 각 문단의 확률값 저장
        paragraph_probabilities = []

        # print('문단 개수 : ', len(paragraphs))

        for paragraph in paragraphs:
            real_prob, fake_prob = predict_text(model, paragraph, tokenizer)
            paragraph_probabilities.append([real_prob, fake_prob])
            #print(f"Paragraph: {paragraph}")

        # 각 문단별 확률 확인
        #print(f"Paragraph probabilities: {paragraph_probabilities}")

        # 5. 소프트 보팅 수행
        voting_results = soft_voting(paragraph_probabilities)
        # print(f"Soft Voting Results - Real: {voting_results['real_probability']}, Fake: {voting_results['fake_probability']}")

        # 작업 완료 상태 업데이트
        tasks[task_id]["status"] = "COMPLETED"

        # 반환값 수정해야 됌. !!
        # tasks[task_id]["result"] = { "real_probability": voting_results['real_probability'], "fake_probability": voting_results['fake_probability'] }

        score = int(voting_results['real_probability'] * 100)

        paragraph_prob_with_text = list(zip(paragraph_probabilities, paragraphs))
        '''
        [
        [[0.7, 0.3],   "첫 번째 문단의 내용입니다."],
        [[0.4, 0.6],   "두 번째 문단의 내용입니다."]
        ]
        '''

        evidence = ""
        if score >= 50:
            # real_prob가 가장 높은 문단 찾기 (real_prob가 첫 번째 인덱스)
            evidence = max(paragraph_prob_with_text, key=lambda x: x[0][0])[1]
        else:
            # fake_prob가 가장 높은 문단 찾기 (fake_prob가 두 번째 인덱스)
            evidence = max(paragraph_prob_with_text, key=lambda x: x[0][1])[1]

        tasks[task_id]["result"] = {
                                    "requestId":task_id,
                                    "blogUrl":url,
                                    "summaryTitle" : title_summary,
                                    "summaryText" : content_summary,
                                    "score" : score,
                                    "evidence": evidence
                                    }

        #print('*** 1 : process_task_id 실행 전 ***')

        await process_task(task_id)

    except Exception as e:
        tasks[task_id]["status"] = "FAILED"
        tasks[task_id]["result"] = str(e)


# 테스트
import asyncio

async def main():
    # Selenium WebDriver 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드
    chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 안 함 (Docker에서 메모리 문제 해결)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # 테스트용 task_id와 url
    task_id = "123e4567-e89b-12d3-a456-426614174000"
    url = "https://blog.naver.com/tkdtkdgns1/223604228666"
    # url = "https://m.blog.naver.com/rose_haus/223058567929"  # 파싱 에러
    # url = "https://blog.naver.com/till0312/223670391764"

    # tasks 초기화
    tasks[task_id] = {"status": "PENDING", "result": None}

    try:
        # process_and_predict_from_url 함수를 await로 호출
        result = await process_and_predict_from_url(task_id, url, driver)

        # 결과 확인
        print(tasks[task_id])
        print('-------')
        print(result)

    finally:
        # 드라이버 종료
        driver.quit()

if __name__ == "__main__":
    # asyncio.run()을 사용하여 비동기 main 함수 실행
    asyncio.run(main())