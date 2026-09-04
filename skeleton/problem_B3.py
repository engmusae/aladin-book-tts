import os
import requests
import json
from pathlib import Path
from gtts import gTTS
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

# 1. 알라딘 API 키
MY_TTBKEY = os.getenv('MY_TTBKEY')

# 2. 알라딘 검색 API URL
ALADIN_SEARCH_URL = 'https://www.aladin.co.kr/ttb/api/ItemSearch.aspx'


# 3. 주제별 도서 데이터 가져오기
def fetch_books_by_topic(topic, max_results=30):
    params = {
        'ttbkey': MY_TTBKEY,
        'Query': topic,
        'QueryType': 'Title',
        'MaxResults': max_results,
        'start': 1,
        'SearchTarget': 'Book',
        'output': 'js',
        'Version': '20131101',
    }

    response = requests.get(
        url=ALADIN_SEARCH_URL,
        params=params
    )

    return response.json()


# 4. 도서 정보를 JSON 파일로 저장
def save_books_to_json(books, filename, max_save=5):
    book_list = []

    for book in books:

        # description이 있는 책만 저장
        if book.get('description'):

            book_info = {
                '제목': book['title'],
                '요약': book['description']
            }

            book_list.append(book_info)

        # 5개가 모이면 종료
        if len(book_list) == max_save:
            break

    # output 폴더 생성
    output = Path('skeleton/output')
    output.mkdir(parents=True, exist_ok=True)

    # JSON 저장
    file_path = output / filename

    with file_path.open('w', encoding='utf-8') as json_file:
        json.dump(
            book_list,
            json_file,
            ensure_ascii=False,
            indent=4
        )

    return book_list


# 5. text를 MP3 파일로 변환
def create_tts_file(text, filename):

    tts = gTTS(
        text=text,
        lang='ko',
        slow=False
    )

    output = Path('skeleton/output')
    output.mkdir(parents=True, exist_ok=True)

    file_path = output / filename

    tts.save(str(file_path))


# 6. 한국문학 도서 처리
def process_korean_literature_books():

    # 6.1 한국문학 검색
    books = fetch_books_by_topic('한국문학').get('item', [])

    # 6.2 description이 있는 책 5개만 JSON 저장
    books = save_books_to_json(
        books,
        'korean_literature_books.json',
        max_save=5
    )

    # 6.3 저장된 5권만 MP3 생성
    for i, book in enumerate(books, 1):

        text = (
            f"제목은 {book['제목']}입니다. "
            f"요약은 {book['요약']}입니다."
        )

        file_name = f'book_{i}.mp3'

        create_tts_file(
            text,
            file_name
        )

    # 6.4 완료 메시지
    print(
        f"{len(books)}개의 책 정보를 처리하고 "
        "음성 파일로 저장했습니다."
    )


# 함수 실행
if __name__ == '__main__':
    process_korean_literature_books()