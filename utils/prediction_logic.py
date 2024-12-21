from utils.summarize import generate_title_summary, generate_text_summary
from utils.task_logic import process_task
from utils.shared import tasks
from utils.crawling import parse_html, crawl_url
from utils.model_utils import load_model_and_tokenizer, predict_text
from utils.preprocess import TextProcessor, split_text_into_paragraphs
from utils.soft_voting import soft_voting

def process_and_predict_from_url(task_id: str, url: str, driver):
    try:
        tasks[task_id]["status"] = "IN_PROGRESS"
        success = True  # 처리 성공 여부를 추적하는 플래그

        # 1. 크롤링 수행
        soup = parse_html(driver, url)
        if soup is None:
            tasks[task_id]["status"] = "FAILED"
            tasks[task_id]["result"] = "HTML 파싱에 실패했습니다."
            success = False

        raw_text = ""
        if success:
            raw_text = crawl_url(soup)
            if not raw_text:
                tasks[task_id]["status"] = "FAILED"
                tasks[task_id]["result"] = "크롤링된 본문 데이터가 비어있습니다."
                success = False

        # 2. 전처리 수행
        processed_text = ""
        title_summary = ""
        content_summary = ""

        if success:
            processor = TextProcessor()
            processed_text = processor.process_text(raw_text)

            # 2-1. 전처리 된 텍스트 요약하기
            try:
                title_summary = generate_title_summary(processed_text)
                content_summary = generate_text_summary(processed_text)
            except Exception as e:
                tasks[task_id]["status"] = "FAILED"
                tasks[task_id]["result"] = f"텍스트 요약 중 오류가 발생했습니다: {str(e)}"
                success = False

        if success and not processed_text.strip():
            tasks[task_id]["status"] = "FAILED"
            tasks[task_id]["result"] = "전처리된 본문 데이터가 비어있습니다."
            success = False

        if success:
            try:
                # 3. 텍스트를 문단으로 나누기
                model, tokenizer = load_model_and_tokenizer()
                paragraphs = split_text_into_paragraphs(processed_text, tokenizer)

                # 4. 모델 로드 및 예측
                model.eval()
                paragraph_probabilities = []

                for paragraph in paragraphs:
                    real_prob, fake_prob = predict_text(model, paragraph, tokenizer)
                    paragraph_probabilities.append([real_prob, fake_prob])

                # 5. 소프트 보팅 수행
                voting_results = soft_voting(paragraph_probabilities)

                # 성공적으로 처리됨
                tasks[task_id]["status"] = "COMPLETED"

                score = int(voting_results['real_probability'] * 100)
                paragraph_prob_with_text = list(zip(paragraph_probabilities, paragraphs))

                evidence = ""
                if score >= 50:
                    evidence = max(paragraph_prob_with_text, key=lambda x: x[0][0])[1]
                else:
                    evidence = max(paragraph_prob_with_text, key=lambda x: x[0][1])[1]

                tasks[task_id]["result"] = {
                    "requestId": task_id,
                    "blogUrl": url,
                    "summaryTitle": title_summary,
                    "summaryText": content_summary,
                    "score": score,
                    "evidence": evidence
                }

            except Exception as e:
                tasks[task_id]["status"] = "FAILED"
                tasks[task_id]["result"] = f"모델 처리 중 오류가 발생했습니다: {str(e)}"
                success = False

    except Exception as e:
        tasks[task_id]["status"] = "FAILED"
        tasks[task_id]["result"] = str(e)

    # 모든 상황에서 항상 실행되어야 함
    process_task(task_id)
