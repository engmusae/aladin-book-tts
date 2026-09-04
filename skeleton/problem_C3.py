import os
import requests
from pathlib import Path
from gtts import gTTS
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv()

MY_TTBKEY = os.getenv('MY_TTBKEY')

ALADIN_SEARCH_URL = 'https://www.aladin.co.kr/ttb/api/ItemSearch.aspx'


# 2. 음악 관련 도서 검색
def fetch_books_by_topic(topic, max_results=10):
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
        ALADIN_SEARCH_URL,
        params=params
    )

    return response.json()


# 3. 도서 정보를 txt 파일로 저장
def save_books_info(books, filename):
    output = Path('skeleton/output')
    output.mkdir(parents=True, exist_ok=True)

    file_path = output / filename

    # 책 10권의 정보를 저장할 문자열 리스트
    contents = []

    for book in books:
        title = book.get('title', '')
        author = book.get('author', '')
        description = book.get('description', '')

        content = (
            f"제목: {title}, "
            f"저자: {author}, "
            f"책 소개: {description}"
        )

        contents.append(content)

    # 한 권당 한 줄씩 저장
    text = '\n'.join(contents)

    with file_path.open('w', encoding='utf-8') as text_file:
        text_file.write(text)

    print(f"{file_path} 파일이 생성되었습니다.")

    # 이후 TTS에서 사용할 수 있도록 파일 경로 반환
    return file_path


# 4. 저장된 txt 파일을 mp3로 변환
def create_audio_file(text_file, audio_file):
    # txt 파일 읽기
    with Path(text_file).open('r', encoding='utf-8') as file:
        text = file.read()

    # gTTS를 이용하여 한국어 음성 생성
    tts = gTTS(
        text=text,
        lang='ko',
        slow=False
    )

    output = Path('skeleton/output')
    output.mkdir(parents=True, exist_ok=True)

    audio_path = output / audio_file

    tts.save(str(audio_path))

    print(f"{audio_path} 파일이 생성되었습니다.")


# 5. 음악 도서 처리
def process_music_books():
    # 5.1 음악 관련 도서 10개 검색
    data = fetch_books_by_topic(
        '음악',
        max_results=10
    )

    books = data.get('item', [])

    # 혹시 API가 10개보다 많이 반환하는 상황에 대비
    books = books[:10]

    # 5.2 txt 파일 생성
    text_file = save_books_info(
        books,
        'music_books_info.txt'
    )

    # 5.3 txt 파일 → mp3
    create_audio_file(
        text_file,
        'music_books.mp3'
    )

    print("모든 작업이 완료되었습니다.")


# 함수 실행
if __name__ == '__main__':
    process_music_books()