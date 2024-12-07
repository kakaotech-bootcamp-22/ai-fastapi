import openai
import os
from dotenv import load_dotenv
import json

from aws_config import get_ssm_parameter

# # .env 파일에서 API 키 로드
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")  # API 키를 OpenAI 클라이언트에 설정

# 백엔드 테스트 파라미터 경로
openai_api_key = "/config/ktb22/OPENAI_API_KEY"

# 각 파라미터 값 가져오기
openai.api_key = get_ssm_parameter(openai_api_key)

def generate_summary(content: str) -> dict:
    """
    OpenAI GPT를 활용하여 블로그 제목과 요약을 생성.

    Args:
        content (str): 블로그 본문 내용

    Returns:
        dict: 제목과 요약을 포함하는 결과
    """
    try:
        model = "gpt-4o-mini"

        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "간단 명료하게, 그리고 재치 있게 본문 내용을 토대로 제목과 본문을 요약해 줘. 그리고 제목과 본문을 각각 JSON 형태로 반환해 줘. JSON 형식을 반드시 지켜야 해. JSON 응답만 반환해. 형식이 깨지지 않도록 주의해. 본문 말투는 친근한 어투로 부탁해."},
                {"role": "user",
                 "content": f"Content: {content}\n\n 이 본문 내용을 토대로, 한 줄을 넘어가지 않는 요약된 제목과 2문장에서 최대 3~4문장인 본문 요약을 작성해줘.\n\nJSON 형식으로 작성:\n{{\"Title\": \"요약된 제목\", \"Summary\": \"요약된 본문\"}}"}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # 결과를 JSON으로 파싱
        result = response['choices'][0]['message']['content'].strip()
        '''
        result 예시
        
        {
            "Title": "하남 코스트코 근처 맛집 하쿠야",
            "Summary": "하남 코스트코 근처 일본 가정식 맛집 하쿠야에서 돈가스를 맛보세요! 아늑한 분위기와 정갈한 메뉴로 추천."
        }
        '''
        print('result :: ', result)

        try:
            parsed_result = json.loads(result)  # JSON 파싱
            print('** parsed_result :: ', parsed_result)
        except json.JSONDecodeError:
            print("JSON Decode Error: 응답을 파싱할 수 없습니다. 응답 내용:", result)
            # JSON 문자열 수정 시도
            result = result.replace("'", '"')  # 작은따옴표를 큰따옴표로 변경
            parsed_result = json.loads(result)  # 다시 파싱 시도

        return parsed_result

    except Exception as e:
        print(f"Error during summary generation: {e}")
        return {"error": str(e)}

# 테스트 실행
if __name__ == "__main__":
    sample_content = """
    하남 코스트코 근처 미사역 맛집 일본가정식 하쿠야 하쿠야 #미사역 맛집 # 미사역 맛집 하남 코스트코에 장 보러 갔다가 저녁 먹으러 다녀왔던 돈가스 맛집 하쿠야!
    """
    result = generate_summary(sample_content)
    print(result)
