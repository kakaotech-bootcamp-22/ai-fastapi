from bs4 import BeautifulSoup
import requests
import re


async def crawl_url(url):
    """
    입력된 URL에서 본문 데이터를 크롤링합니다 (비동기).
    Args:
        url (str): 크롤링할 URL.
    Returns:
        str: 크롤링된 본문 텍스트.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리

        soup = BeautifulSoup(response.text, 'html.parser')

        # 텍스트 데이터 수집
        content = soup.find_all('p', class_=re.compile('se-text-paragraph'))

        # 본문 내용만 리스트로 저장
        article_content = []
        for item in content:
            paragraphs = item.find_all('span')  # 본문 텍스트는 span 태그 안에 있을 가능성이 높음
            for paragraph in paragraphs:
                chunk = paragraph.get_text(strip=True)
                chunk = chunk.replace(u"\u200b", u"\n")
                article_content.append(chunk)

        whole_text = ' '.join(article_content)

        # 수정: whole_text 반환
        return whole_text
    except Exception as e:
        raise RuntimeError(f"크롤링 실패: {str(e)}")
