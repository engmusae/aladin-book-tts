import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# 1. [ 환경 변수 로드 ]
load_dotenv()
MY_TTBKEY = os.getenv('MY_TTBKEY')
ALADIN_SEARCH_URL = 'https://www.aladin.co.kr/ttb/api/ItemSearch.aspx'

# 2. [ 최대 100개까지 주제별 도서 데이터를 가져오는 함수 정의 ]
def fetch_books_by_topic(topic, max_results=100):
    url = ALADIN_SEARCH_URL 
    params = {
        'TTBKey': MY_TTBKEY,    # API 키 정보
        'Query': topic,       # 검색할 키워드 정보
        'Output': 'js',         # 응답 형식 (JSON)
        'Version': '20131101',  # API 버전
        'MaxResults': max_results # 최대 결과 개수
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

# 3. '인공지능' 도서 데이터를 처리하는 함수 정의
def process_ai_books():
    # 3.1 [ '인공지능' 관련 도서 검색 ]
    # fetch_books_by_topic()을 호출하여 '인공지능' 관련 도서를 100개 수집합니다.
    ai_books = fetch_books_by_topic('인공지능', max_results=100)  

    # 3.2 [ 수집된 데이터에서 가격 정보가 있는 책 필터링 및 가격순 정렬 ]
    ai_books = ai_books.get('item', [])
    valid_books = [ai_book for ai_book in ai_books if ai_book.get('priceStandard', 0) > 0]
    sorted_books = sorted(valid_books, key=lambda ai_book: ai_book['priceStandard'], reverse=True)

    # 3.3 [ 상위 10개 도서 선택 ]
    ai_top10_books = sorted_books[:10]

    # 3.4 [ 상위 10개 도서 정보 출력 ]
    print(ai_top10_books)

    # 3.5 [ JSON 파일로 저장할 데이터 준비 ]
    # output/ai_top10_books.json 파일로 저장
    file_path = 'output/ai_top10_books.json'
    path = Path(file_path)
    path.write_text(json.dumps(ai_top10_books, ensure_ascii=False, indent=4), encoding='utf-8')
        
    # 3.6 [ 완료 메시지를 출력 ]
    print("ai_top10_books.json 파일 저장 완료")

# 함수 실행
if __name__ == '__main__':
    process_ai_books()