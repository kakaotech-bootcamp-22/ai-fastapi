import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def parse_html(driver, url):
    try:
        # URL에 접속
        driver.get(url)
        time.sleep(3)  # 페이지 로딩 대기 (필요시 조정)

        # iframe으로 전환
        iframe = driver.find_element(By.ID, "mainFrame")  # id="mainFrame"인 iframe 찾기
        driver.switch_to.frame(iframe)  # iframe 전환

        # BeautifulSoup로 HTML 파싱
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

    except Exception as e:
        print(f"HTML 파싱 실패: {e}")
        return None



# async def crawl_url(soup): 비동기로 나중에 수정 -> 테스트 위해서 잠시 빼둠
def crawl_url(soup):
    """
    BeautifulSoup 객체에서 본문 데이터를 크롤링합니다.
    Args:
        soup (BeautifulSoup): 파싱된 HTML 데이터.
        url (str): 크롤링할 URL.
    Returns:
        str: 크롤링된 본문 텍스트.
    """
    try:
        if soup is None:
            raise ValueError("BeautifulSoup 객체가 None입니다.")

        # 본문 데이터를 크롤링
        content = soup.find_all('p', class_=re.compile('se-text-paragraph'))
        if not content:
            raise ValueError("본문 데이터를 찾을 수 없습니다.")

        # 본문 내용 추출
        article_content = []
        for item in content:
            paragraphs = item.find_all('span')  # 본문 텍스트는 span 태그 안에 있음
            for paragraph in paragraphs:
                chunk = paragraph.get_text(strip=True)
                chunk = chunk.replace(u"\u200b", u"\n")  # 제어 문자 제거
                article_content.append(chunk)

        whole_text = ' '.join(article_content)
        if not whole_text.strip():
            raise ValueError("본문 텍스트가 비어 있습니다.")

        return whole_text

    except Exception as e:
        print(f"크롤링 실패: {e}")
        return None
