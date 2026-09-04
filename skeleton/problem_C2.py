import os
import requests
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 1. [ 환경 변수 로드 ]
load_dotenv()
MY_TTBKEY = os.getenv('MY_TTBKEY')
ALADIN_SEARCH_URL = 'https://www.aladin.co.kr/ttb/api/ItemSearch.aspx'
OPENAI_API_KEY = os.getenv('MY_API_KEY')


# 2. OpenAI API 클라이언트 초기화
client = OpenAI(
    base_url='https://gms.ssafy.io/gmsapi/api.openai.com/v1',
    api_key=OPENAI_API_KEY
)

# 3. [ 최대 100개까지 주제별 도서 데이터를 가져오는 함수 정의 ]
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
    books = response.json()
    return books

# 4. 책 데이터를 ChatGPT로 분류하는 함수 정의 (습관, 시간관리, 독서법, 기타)
def classify_books_with_gpt(books):
    # 4.1 [ 분류할 책 제목들을 전달하기 편한 문자열로 취합 ]
    books = books.get('item', [])
    titles = []
    for book in books:
        title = book['title']
        titles.append(title)
    titles_text = "\n".join(titles)
    print(titles_text)

    # 4.2 [ ChatGPT 대화 메시지 설정 (프롬프트 작성) ]
    # 습관, 시간관리, 독서법, 기타 로 분류
    conversation_history = [
        {
            "role": "system", 
            "content": (
                "당신은 도서 제목 목록을 받아 카테고리별로 분류하는 시스템입니다. "
                "반드시 제시된 도서들을 '습관', '시간관리', '독서법', '기타' 4개의 키를 가진 JSON 객체로 분류하여 결과만 출력하세요."
            )
        },
        {
            "role": "user",
            "content": f"다음 책 제목들을 '습관', '시간관리', '독서법', '기타' 카테고리로 분류해서 JSON으로 출력해줘:\n\n{titles_text}"
        }
    ]

    # 4.3 [ 생성형 AI에 분류 요청 보내기 ]
    # client.chat.completions.create() 호출 (example 코드 참고)
    response = client.chat.completions.create(
    model="gpt-5-nano",             # 사용하려는 모델 (필수 지정)
    messages=conversation_history,  # 대화 메시지 목록 (필수 지정)
    max_completion_tokens=4080,     # 생성될 응답의 최대 토큰 수 (값의 범위: 1~모델 마다 최대값 ex> gpt-4o-mini: 16,385 tokens)
    temperature=1.0,                # 확률 분포 조정을 통한 응답의 다양성 제어 (값의 범위: 0~2)
    top_p=1.0,                      # 누적 확률 값을 통한 응답의 다양성 제어 (값의 범위: 0~1)
    n=1,                            # 생성할 응답 수 (1이상의 값)
    seed=1000,                       # 랜덤 씨드 값 (설정하는 경우 일관된 답변을 얻을 수 있음)
    response_format = {"type": "json_object"}) 

    # 4.4 [ ChatGPT의 응답을 가져와 JSON 으로 추출 ]
    # ! 주의. JSON 형태로 프롬프팅을 하지 못하면 파싱에서 에러가 발생할 수 있습니다.
    result_text = response.choices[0].message.content  # 응답에서 JSON 데이터를 추출하고 파싱
    classification = json.loads(result_text)
    return classification   # 분류 정보 반환


# 5. [ 데이터를 JSON 파일로 저장하는 함수 정의 ]
def save_to_json(data, filename):
    output_folder = Path('output')
    file_path = output_folder / filename
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=4), 
        encoding='utf-8'
    )    

# 6. '독서' 도서 데이터를 처리하는 함수 정의
def process_reading_books():
    # 6.1 [ '독서'와 관련된 도서 검색 (100개) ]
    books_data = fetch_books_by_topic('독서', max_results=100)  # fetch_books_by_topic() 호출

    # 6.2 [ 생성형 AI를 이용해 책 분류 ]
    classification = classify_books_with_gpt(books_data)  # classify_books_with_gpt() 호출

    # 6.3 [ 분류된 책 정보를 JSON 파일로 저장 ]
    # output/reading_habits.json 으로 저장하기
    save_to_json(classification, 'reading_habits.json')  # save_to_json() 호출

    # 완료 메시지 출력
    print("'output/reading_habits.json' 파일 생성 완료")


# 함수 실행
if __name__ == '__main__':
    process_reading_books()