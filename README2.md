# 📚 알라딘 API & OpenAI GPT 연동 도서 자동 분류 시스템 개발기

본 프로젝트는 **알라딘 Open API**로 최신 도서 데이터를 수집하고, **OpenAI GPT API(GMS)**를 활용하여 수집된 책들을 특정 카테고리(`습관`, `시간관리`, `독서법`, `기타`)로 자동 분류한 뒤 결과를 JSON 파일로 저장하는 파이프라인 개발 과정 및 회고 기록입니다.

---

## 📌 목차
1. [프로젝트 개요](#-프로젝트-개요)
2. [단계별 구현 과정 & 핵심 코드](#-단계별-구현-과정--핵심-코드)
3. [💡 단계별 주요 학습 내용](#-단계별-주요-학습-내용)
4. [🚨 발생했던 에러 및 디버깅](#-발생했던-에러-및-디버깅)
5. [✨ 새로 배운 것들 및 총평 (느낀 점)](#-새로-배운-것들-및-총평-느낀-점)

---

## 🛠️ 프로젝트 개요

* **목적**: '독서' 관련 도서 100권을 수집한 뒤, 생성형 AI(LLM)를 통해 도서 제목을 분석하고 주제별로 분류하여 가공된 데이터 파일(`output/reading_habits.json`) 생성
* **주요 기술 스택**: `Python 3.11`, `requests`, `openai (v1.x)`, `python-dotenv`, `pathlib`
* **사용한 API**: 알라딘 Open API (ItemSearch), OpenAI API (GMS 엔드포인트)

---

## 🏗️ 단계별 구현 과정 & 핵심 코드

### 코드 스크린샷
![A1](.\images\A1.png)
![A2](.\images\A2.png)
![A3](.\images\A3.png)
![C1](.\images\C1.png)
![C2](.\images\C2_1.png)
![C2](.\images\C2_2.png)
![C2](.\images\C2_3.png)

### Step 1. 환경 변수 설정 및 보안 관리
API Key와 URL을 코드에 직접 노출하지 않고 `.env` 파일에 분리하여 관리하도록 설정했습니다.

```python
import os
from dotenv import load_dotenv

load_dotenv()
MY_TTBKEY = os.getenv('MY_TTBKEY')
OPENAI_API_KEY = os.getenv('MY_API_KEY')
```

### Step 2. 알라딘 API 연동 도서 수집 (fetch_books_by_topic)
검색 키워드('독서')와 최대 결과 수(100개)를 파라미터로 설정하여 알라딘 API 서버로 GET 요청을 보냅니다.

```python
def fetch_books_by_topic(topic, max_results=100):
    url = '[https://www.aladin.co.kr/ttb/api/ItemSearch.aspx](https://www.aladin.co.kr/ttb/api/ItemSearch.aspx)'
    params = {
        'TTBKey': MY_TTBKEY,
        'Query': topic,
        'Output': 'js',
        'Version': '20131101',
        'MaxResults': max_results
    }
    response = requests.get(url, params=params)
    return response.json()
```

### Step 3. OpenAI GPT 연동 도서 카테고리 분류 (classify_books_with_gpt)
수집한 도서 데이터의 제목들만 리스트 형태로 추출하고, 이를 하나의 텍스트(\n 구분)로 묶어 GPT 모델에 전달합니다.

```python
def classify_books_with_gpt(books):
    # 1. 도서 제목 추출 및 문자열 결합
    books_list = books.get('item', [])
    titles = [book['title'] for book in books_list]
    titles_text = "\n".join(titles)

    # 2. 프롬프트 구성
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

    # 3. GPT API 호출 및 JSON 구조 응답 처리
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=conversation_history,
        max_completion_tokens=4080,
        temperature=1.0,
        response_format={"type": "json_object"}
    )

    result_text = response.choices[0].message.content
    return json.loads(result_text)
```

### Step 4. 결과 데이터 JSON 파일 저장 (save_to_json)
분류된 결과를 output 폴더 경로에 한글이 깨지지 않는 UTF-8 인코딩 형식으로 저장합니다.    

```python
def save_to_json(data, filename):
    output_folder = Path('output')
    output_folder.mkdir(exist_ok=True)  # 폴더가 없을 경우 자동 생성
    
    file_path = output_folder / filename
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=4), 
        encoding='utf-8'
    )
```

## 💡 단계별 주요 학습 내용

### 1. External API Data Normalization (외부 API 데이터 정규화)
* 알라딘 API 응답 데이터 구조 중 실제 필요한 도서 배열 객체가 `item` 키에 담겨 들어오는 패턴을 파악하고, `books.get('item', [])` 방식의 방어적 프로그래밍 기법을 익혔습니다.

### 2. LLM Prompting & Controlled Output (생성형 AI 제어 기법)
* LLM은 기본적으로 자유 형식의 텍스트(Unstructured Text)를 출력하므로, 파이썬 코드에서 다시 파싱하려면 응답을 **구조화(Structured)**해야 한다는 점을 배웠습니다.
* `response_format={"type": "json_object"}` 옵션과 함께 `system` 메시지에 역할과 카테고리 Key 이름을 명확히 전달함으로써 안정적인 JSON 응답을 받아내는 노하우를 습득했습니다.

### 3. Pathlib & Modern Python File I/O
* 기존 `open()` / `close()` 방식 대신 `pathlib.Path` 모듈을 활용하여 파일/폴더 생성 및 텍스트 쓰기(`write_text`)를 직관적이고 깔끔한 코드로 처리하는 법을 익혔습니다.

---

## 🚨 발생했던 에러 및 디버깅

### 1. `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`
* **발생 상황**: `classify_books_with_gpt()` 내부의 `json.loads(result_text)` 구문 실행 시 파싱 에러 발생
* **원인 분석**:
  * GPT API 프롬프트에 `f-string` 접두사(`f""`)가 누락되어 실제 책 제목 데이터가 전달되지 않고 `"{titles_text}"`라는 리터럴 문자열이 넘어감.
  * GPT가 분류할 대상을 받지 못하여 *"분류할 목록을 입력해주세요"*라는 일반 대화형 문장을 출력함.
  * 텍스트 형태의 응답을 `json.loads()`로 해석하려다 첫 번째 글자부터 JSON 규칙에 맞지 않아 `JSONDecodeError` 발생.
* **해결 방법**:
  * 프롬프트 문자열 앞에 `f`를 명시하여 `f"...\n\n{titles_text}"` 형태로 변수값이 제대로 바인딩되도록 수정.
  * `try-except json.JSONDecodeError` 구문을 추가하여 GPT 응답 파싱 실패 시 원본 응답 문장을 로깅하도록 방어 코드 작성.

### 2. 파이썬 내장 객체 이름 오버라이딩(Name Shadowing) 문제
* **발생 상황**: 책 제목 데이터를 수집하는 과정에서 `.join()`이나 `.append()` 동작 에러 발생
* **원인 분석**: `str = book['title']` 형태로 변수명을 파이썬 기본 예약어/타입명인 `str`로 정의하여 `str()` 함수 및 기존 타입 관련 메소드가 재정의되는 버그 발생.
* **해결 방법**: `title = book['title']`처럼 명확하고 의미 있는 단어로 변수명을 변경하고, `titles`라는 리터럴 리스트 객체를 생성하여 `.append()` 후 `"\n".join(titles)`로 안전하게 처리함.

### 3. `FileNotFoundError` (출력 디렉토리 미존재)
* **발생 상황**: `output/reading_habits.json` 파일 저장 시 폴더를 찾지 못해 에러 발생
* **원인 분석**: `output` 폴더가 디렉토리에 미리 존재하지 않은 상태에서 파일 생성을 시도함.
* **해결 방법**: `Path('output').mkdir(exist_ok=True)` 옵션을 사용하여 폴더가 없을 경우 자동으로 생성하도록 보완.

---

## ✨ 새로 배운 것들 및 총평 (느낀 점)

### 🧠 새로 배운 핵심 포인트
* **API 파이프라인 구조화**: 외부 서비스 API(알라딘)로 데이터를 가져와 또 다른 서비스 API(OpenAI)로 가공한 뒤 내보내는 '데이터 처리 파이프라인'의 전반적인 구성을 직접 만들어볼 수 있었습니다.
* **LLM을 단순 대화창이 아닌 프로그램 함수로 다루기**: GPT API를 단순 질의응답용이 아닌, 텍스트 데이터 분류/가공용 비즈니스 로직의 한 블록(Function)으로 활용하는 패턴을 정립했습니다.
* **디버깅 과정에서의 원인 추적 능력**: `JSONDecodeError`가 발생했을 때 단순히 코드가 틀렸다고 생각하는 대신, 'API 호출값 ➔ GPT 응답 문자열 ➔ 파싱' 단계를 하나씩 들여다보며 실제 파싱 대상 데이터가 무엇이었는지 추적하는 디버깅 역량을 키웠습니다.

### 📝 개발 소회 & 느낀 점
* 처음에는 API 호출 후 `json.loads()`를 실행할 때 무작정 에러가 발생해서 막막했습니다. 하지만 에러 로그가 가리키는 라인을 추적하고 GPT가 실제 반환한 `result_text`를 직접 출력해보면서, 에러의 본질이 **"파이썬 코드가 아니라 GPT에게 보낸 프롬프트(f-string)의 실수"**에 있었다는 것을 깨달았습니다.
* LLM API를 연동할 때는 프로그램 코드의 엄격함과 AI 모델의 유연함 사이에 차이가 존재하므로, `response_format` 설정과 예외 처리가 얼마나 중요한지 몸소 배울 수 있었던 뜻깊은 프로젝트였습니다.