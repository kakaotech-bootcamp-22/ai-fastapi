import openai
from aws_config import get_ssm_parameter

# 백엔드 테스트 파라미터 경로
openai_api_key = "/config/ktb22/OPENAI_API_KEY"

# 각 파라미터 값 가져오기
openai.api_key = get_ssm_parameter(openai_api_key)

def generate_title_summary(content: str) -> dict:
    try:
        model = "gpt-4o-mini"

        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system",
                 "content": "간단 명료하게, 그리고 재치 있게 본문 내용을 토대로 요약된 제목을 생성해 줘. 본문 말투는 친근한 어투로 부탁해."},
                {"role": "user",
                 "content": f"Content: {content}\n\n 이 본문 내용을 토대로, 한 줄을 넘어가지 않는 간단하고 요약된 제목을 작성해 줘."}
            ],
            max_tokens=500,
            temperature=0.7
        )
        title = response['choices'][0]['message']['content']
        print('제목 요약 :: ', title)
        return title

    except Exception as e:
        print(f"Error during summary generation: {e}")
        return {"error": str(e)}

def generate_text_summary(content: str) -> dict:
    try:
        model = "gpt-4o-mini"

        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "간단 명료하게, 그리고 재치 있게 본문 내용을 요약해줘. 본문 말투는 친근한 어투로 부탁해."},
                {"role": "user",
                 "content": f"Content: {content}\n\n 이 본문 내용을, 2문장에서 최대 3 ~ 4 문장으로 이루어진 요약을 작성해줘."}
            ],
            max_tokens=500,
            temperature=0.7
        )
        text = response['choices'][0]['message']['content']
        print('제목 요약 :: ', text)
        return text

    except Exception as e:
        print(f"Error during summary generation: {e}")
        return {"error": str(e)}

# 테스트 실행
if __name__ == "__main__":
    sample_content = """
    [부대찌개대사관 선릉직영점] 선릉역 점심 맛집 리뷰[SEP]
    오늘은 선릉 부찌 맛집 '부대찌개대사관 선릉직영점' 리뷰입니다.[SEP]
    부대찌개대사관 외관[SEP]
    외관이에요.[SEP]
    못 찾기도 어려운 1층에 자리하고 있어용☺ 연중 무휴 식당이고 브레이크타임만 피하면 돼요![SEP]
    브레이크 타임은 09시~10시와 16시~17시 두 타임이에요.[SEP]
    참고로 여기는 맛있는 녀석들 맛집…![SEP]
    생방송투데이 방영 맛집인 것도 안 비밀🤫[SEP]
    내부는 생각보다 크고 테이블도 많아요.[SEP]
    그리고 무엇보다 좋았던 건 정말 깨끗해요!![SEP]
    사진은 나올 때 찍은건데 제가 들어갔을 때는 평일 저녁 기준 만석이었어요.[SEP]
    되게 인테리어가 FANCY하고 깔끔한데 샹들리에가 있을 줄이야😂[SEP]
    부대찌개대사관 메뉴[SEP]
    매장에서는 키오스크 메뉴라 사진이 잘 안 나와서 네이버 지도에 있는 메뉴 사진으로 대체합니다![SEP]
    야근 이슈로 안주로 찰떡같아 보였던 돌판목쏘한판을 스킵했지만 정말 괜찮아보였어요[SEP]
    🍺💛[SEP]
    부대찌개대사관 햄 종류[SEP]
    햄은 세 가지 종류인데요[SEP]
    사진 참고하세요.[SEP]
    저는 어렸을 때부터 촙트햄이 가장 좋더라구요[SEP]
    💓[SEP]
    저는 두 명이서 방문했고 - 대사관부대찌개 2인(공기밥 포함)(1.3*2 = 2.6) - 라면사리 1개(0.2) - 카스 1병(0.6) 주문했어요.[SEP]
    리뷰이벤트 & 맛있게 먹는 팁[SEP]
    아니 리뷰이벤트 인원수만큼 참여 가능인데 너무 이득 아니냐면서…[SEP]
    부찌집에서 밥 조금 주는 거 싫어하는데 여긴 손크기만한 밥그릇이 나와요[SEP]
    🤭[SEP]
    일단 목부터 축이고… 고생했다[SEP]
    오늘도^^..[SEP]
    드디어 나온 대사관부대찌개…![SEP]
    햄이 정말 무지하게 많아요.[SEP]
    부찌 먹을 때 햄 눈치싸움 누구나 조금씩은 하지 않나요?[SEP]
    여기서는 눈치 볼 일이 없어서 좋았어요[SEP]
    😂[SEP]
    어느 정도 끓으면 직원분이 마늘 넣어주시고 콩나물 올려주셔용😊[SEP]
    겉에 동그란 햄부터 먹고 안에 뒤적뒤적해서 먹으면 되더라구요.[SEP]
    햄 종류도 다양하고 저렴한 햄 맛 나는 게 없어서 만족 하면서 먹었어요![SEP]
    무엇보다 정말 햄 양이 미쳤어요.[SEP]
    라면사리 안 넣으면 유죄…![SEP]
    테이블마다 육수가 따로 있어서 조금 더 부어줬어요.[SEP]
    자고로 부대찌개에 넣어먹는 라면사리는 살짝 덜 익게, 꼬들거리게 먹어야 한다고 생각해요.(단호)[SEP]
    라면사리 다 먹구 남은 야채까지 다 먹어줍니당[SEP]
    🤗 기본적으로 미나리가 듬뿍 들어가있어서 좋았던 것 같아요.[SEP]
    미나리의 향긋한 향이 있고 국물이 전혀 느끼하지 않았어요.[SEP]
    이번에는 체험단으로 다녀왔지만 저도 그렇고 같이 간 동기도 재방문 의사 있다 고 했어요![SEP]
    매장이 정말 깨끗하고 맛도 괜찮은데 퀄리티 대비 가격도 좋아서 그런 것 같아요.[SEP]
    선릉역 부대찌개 맛집으로 인정합니다[SEP]
    🙂 참고로 가맹사업을 시작하게 되었다고 해요.('부대찌개대사관.kr'로 가맹문의)[SEP]
    위치 남기며 마무리할게요.[SEP]
    """
    result1 = generate_title_summary(sample_content)
    result2 = generate_text_summary(sample_content)

    print(result1)
    print(result2)
