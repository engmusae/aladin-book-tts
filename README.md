# 프로젝트 회고

## 1. 프로젝트 개요

이번 프로젝트에서는 알라딘 Open API를 활용하여 도서 데이터를 수집하고, 필요한 정보를 가공하여 JSON 및 TXT 파일로 저장한 뒤, 도서의 제목과 소개 내용을 TTS(Text-to-Speech)로 변환하여 음성 파일을 생성하는 기능을 구현했다.

단순히 API 데이터를 받아 출력하는 것에서 끝나는 것이 아니라 다음과 같은 전체 흐름을 직접 구현했다.

1. `.env`를 활용한 API Key 관리
2. `requests`를 이용한 외부 API 호출
3. JSON 응답 데이터 구조 분석
4. 필요한 도서 정보 필터링 및 가공
5. JSON / TXT 파일 저장
6. `pathlib`을 활용한 디렉터리 및 파일 경로 관리
7. gTTS를 활용한 음성 파일 생성
8. `venv`, `requirements.txt`, `.gitignore`를 활용한 개발 환경 관리
9. GitLab을 이용한 버전 관리

---

# 단계별 구현 과정 및 학습 내용

## 1. API Key와 환경 변수 관리

처음에는 API Key를 코드 내부에 직접 작성할 수도 있었지만, API Key와 같은 민감한 정보는 소스 코드와 분리하여 관리해야 한다는 점을 학습했다.

`.env` 파일에 API Key를 저장하고 다음과 같이 불러왔다.

```env
MY_TTBKEY=발급받은_API_KEY
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

MY_TTBKEY = os.getenv('MY_TTBKEY')
```

구현 과정에서 다음과 같은 오류도 경험했다.

```text
{'errorCode': 1, 'errorMessage': '키를 입력해 주세요'}
```

처음에는 API 자체의 문제라고 생각했지만, 실제로는 `.env` 파일의 값을 정상적으로 읽지 못하거나 환경 변수 이름이 일치하지 않아 API Key가 요청에 전달되지 않은 것이 원인이었다.

이를 통해 API 호출이 실패했을 때는 단순히 요청 URL만 확인하는 것이 아니라 다음 항목도 함께 확인해야 한다는 것을 배웠다.

- `.env` 파일의 위치
- 환경 변수 이름
- `load_dotenv()` 실행 여부
- API 요청에 실제 Key가 전달되는지 여부

또한 `.env`가 GitLab에 올라가지 않도록 `.gitignore`에 다음과 같이 설정했다.

```gitignore
.env
venv/
```

이번 과정을 통해 민감한 정보를 코드와 분리해서 관리하는 것이 실제 프로젝트에서 중요하다는 것을 알게 되었다.

---

## 2. 알라딘 API를 활용한 도서 데이터 수집

`requests` 라이브러리를 사용하여 알라딘 Open API에 HTTP GET 요청을 보냈다.

```python
response = requests.get(
    url=ALADIN_SEARCH_URL,
    params=params
)

data = response.json()
```

처음에는 API 응답 전체를 도서 리스트라고 생각하여 데이터를 처리하는 과정에서 오류가 발생했다.

실제 API 응답은 딕셔너리 형태이며, 도서 목록은 `item`이라는 Key 내부에 리스트 형태로 저장되어 있었다.

```python
books = fetch_books_by_topic('한국문학').get('item', [])
```

이 과정을 통해 외부 API를 사용할 때는 데이터를 가져오는 것보다 먼저 **응답 데이터의 구조를 확인하는 과정이 중요하다**는 것을 배웠다.

또한 다음과 같이 `.get()`을 사용하면 Key가 없는 상황에서도 오류 대신 빈 리스트를 받을 수 있다는 점을 알게 되었다.

```python
.get('item', [])
```

---

## 3. 리스트와 딕셔너리 구조 이해

이번 프로젝트에서 반복적으로 발생했던 오류 중 하나는 다음과 같았다.

```text
TypeError: list indices must be integers or slices, not str
```

예를 들어 다음과 같이 작성했을 때 문제가 발생했다.

```python
books['title']
```

`books`는 여러 권의 책이 들어있는 `list`이고, 각 책 한 권이 `dict` 형태였기 때문이다.

데이터 구조를 단순화하면 다음과 같다.

```python
books = [
    {
        'title': '책1',
        'description': '설명1'
    },
    {
        'title': '책2',
        'description': '설명2'
    }
]
```

따라서 반복문 안에서는 각 책을 의미하는 `book`에 접근해야 했다.

```python
for book in books:
    print(book['title'])
```

이를 통해 API 데이터를 사용할 때는 현재 변수가 `list`인지 `dict`인지 정확히 파악하는 것이 중요하다는 것을 알게 되었다.

앞으로는 오류가 발생했을 때 바로 코드를 수정하기보다 `print()`, `type()`, `pprint()` 등을 활용하여 현재 데이터 구조를 먼저 확인하는 습관이 필요하다고 느꼈다.

---

## 4. `append()`와 `extend()`의 차이

여러 주제의 도서 데이터를 하나의 리스트에 합치는 과정에서 `append()`와 `extend()`의 차이를 명확하게 이해하게 되었다.

다음과 같이 작성하면,

```python
all_books.append(books)
```

리스트 자체가 하나의 요소로 추가된다.

```python
[
    [
        book1,
        book2
    ]
]
```

반면 다음과 같이 작성하면,

```python
all_books.extend(books)
```

리스트 내부의 요소들이 하나씩 추가된다.

```python
[
    book1,
    book2
]
```

처음에는 이 차이를 정확히 이해하지 못해 리스트가 중첩되었고, 이후 데이터에 접근하는 과정에서 오류가 발생했다.

이를 통해 단순히 메서드의 사용법을 외우는 것보다 **메서드를 실행했을 때 자료구조가 어떻게 변경되는지 이해하는 것이 중요하다**는 것을 배웠다.

---

## 5. 도서 데이터 필터링 및 평균값 계산

도서를 할인 도서와 정가 도서로 분류하는 과정에서도 조건문을 정확하게 작성하는 것이 중요했다.

처음에는 다음과 같이 작성했다.

```python
if book['priceSales']:
    discounts.append(book)
```

하지만 `priceSales`는 판매 가격이므로 값이 0이 아닌 경우 Python에서 `True`로 평가된다.

따라서 거의 모든 책이 할인 도서로 분류되는 문제가 발생했다.

실제 할인 여부를 판단하기 위해서는 정가와 판매가를 비교해야 했다.

```python
if book['priceSales'] < book['priceStandard']:
    discounts.append(book)
else:
    regulars.append(book)
```

이를 통해 Python에서 값 자체의 참/거짓 판정과 실제 비교 조건은 다르다는 점을 알게 되었다.

또한 도서 가격이나 출판 연도 등의 평균을 구하면서 다음과 같은 기본 계산 방법도 활용했다.

```python
average = sum(numbers) / len(numbers)
```

기초적인 Python 문법이 실제 데이터를 분석하는 과정에서 직접 활용된다는 점이 인상적이었다.

---

## 6. 필요한 데이터만 가공하여 JSON으로 저장

알라딘 API에서는 많은 도서 정보를 제공하지만, 과제에서는 제목과 요약만 필요했다.

따라서 필요한 정보만 새로운 딕셔너리 형태로 가공했다.

```python
book_info = {
    '제목': book['title'],
    '요약': book['description']
}
```

또한 `description`이 존재하는 책만 선택하고 최대 5권까지만 저장하도록 구현했다.

```python
book_list = []

for book in books:
    if book.get('description'):
        book_info = {
            '제목': book['title'],
            '요약': book['description']
        }

        book_list.append(book_info)

    if len(book_list) == 5:
        break
```

이후 `json.dump()`를 이용해 JSON 파일로 저장했다.

```python
with file_path.open('w', encoding='utf-8') as json_file:
    json.dump(
        book_list,
        json_file,
        ensure_ascii=False,
        indent=4
    )
```

이 과정에서 `ensure_ascii=False`를 사용하면 한글이 Unicode 문자 형태가 아니라 실제 한글로 저장된다는 점을 알게 되었다.

또한 `indent=4`를 사용하여 사람이 읽기 좋은 형태로 JSON 파일을 저장할 수 있었다.

---

## 7. `pathlib`을 활용한 파일 경로 관리

파일을 저장하는 과정에서는 경로 설정과 관련된 오류도 경험했다.

```text
[Errno 13] Permission denied: '\discounted_books.json'
```

파일명 앞에 `/` 또는 `\`를 붙이면서 의도하지 않은 루트 경로에 파일을 저장하려고 한 것이 원인이었다.

이후 `pathlib.Path`를 사용하여 파일 경로를 구성했다.

```python
output = Path('output')
output.mkdir(parents=True, exist_ok=True)

file_path = output / 'discounted_books.json'
```

특히 다음 표현을 통해 파일 경로를 간단하게 연결할 수 있었다.

```python
output / filename
```

또한,

```python
output.mkdir(parents=True, exist_ok=True)
```

를 사용하면 폴더가 존재하지 않는 경우 자동으로 생성할 수 있다는 점도 배웠다.

문자열로 직접 파일 경로를 작성하는 것보다 `Path`를 활용하는 것이 더 읽기 쉽고 안전하다는 것을 느꼈다.

---

## 8. TXT 파일 저장 과정에서의 덮어쓰기 문제

음악 관련 도서 10권의 정보를 TXT 파일에 저장하는 과정에서 처음에는 반복문 안에서 파일을 `'w'` 모드로 열었다.

```python
for book in books:
    with file_path.open('w', encoding='utf-8') as text_file:
        text_file.write(content)
```

하지만 `'w'` 모드는 파일을 열 때마다 기존 내용을 삭제하기 때문에 마지막 도서 정보만 파일에 남는 문제가 발생했다.

이를 해결하기 위해 먼저 각 책의 정보를 리스트에 저장했다.

```python
contents = []

for book in books:
    content = f"제목: {title}, 저자: {author}, 책 소개: {description}"
    contents.append(content)
```

이후 하나의 문자열로 합친 뒤 파일을 한 번만 열어 저장했다.

```python
text = '\n'.join(contents)

with file_path.open('w', encoding='utf-8') as text_file:
    text_file.write(text)
```

이를 통해 파일 입출력에서 `'w'` 모드가 기존 내용을 덮어쓴다는 점을 직접 확인할 수 있었다.

파일을 반복문 안에서 여는 것과 데이터를 먼저 가공한 뒤 한 번에 저장하는 방식의 차이도 이해하게 되었다.

---

## 9. gTTS를 활용한 음성 파일 생성

도서의 제목과 요약 정보를 음성 파일로 만들기 위해 `gTTS`를 사용했다.

```python
tts = gTTS(
    text=text,
    lang='ko',
    slow=False
)

tts.save('book_1.mp3')
```

처음에는 여러 권의 책이 들어 있는 `books` 리스트와 반복문에서 하나의 책을 나타내는 `book`을 혼동하여 오류가 발생했다.

잘못된 접근은 다음과 같았다.

```python
books['title']
```

반복문 안에서는 다음과 같이 현재 책 한 권에 접근해야 했다.

```python
for i, book in enumerate(books, 1):
    text = book['제목'] + book['요약']
```

또한 `enumerate()`를 사용하여 각 파일의 번호를 쉽게 생성할 수 있었다.

```python
file_name = f'book_{i}.mp3'
```

결과적으로 다음과 같이 여러 개의 음성 파일을 생성할 수 있었다.

```text
output/
├── book_1.mp3
├── book_2.mp3
├── book_3.mp3
├── book_4.mp3
├── book_5.mp3
└── korean_literature_books.json
```

또한 음악 관련 도서에서는 여러 권의 책 정보를 하나의 TXT 파일로 저장한 뒤 해당 내용을 하나의 MP3 파일로 변환하는 방식도 구현했다.

```text
output/
├── music_books_info.txt
└── music_books.mp3
```

이를 통해 API에서 가져온 텍스트 데이터를 실제 음성 결과물로 연결하는 전체 흐름을 경험할 수 있었다.

---

# 개발 환경 관리

## 가상환경 생성

프로젝트에서 필요한 라이브러리를 독립적으로 관리하기 위해 Python 가상환경을 생성했다.

```bash
python -m venv venv
```

Git Bash에서는 다음과 같이 활성화했다.

```bash
source venv/Scripts/activate
```

이후 `requirements.txt`를 이용하여 필요한 라이브러리를 설치했다.

```bash
pip install -r requirements.txt
```

가상환경을 사용하면서 프로젝트마다 서로 다른 라이브러리와 버전을 독립적으로 관리하는 이유를 이해할 수 있었다.

---

## `.gitignore` 관리

처음에는 `.env`와 `venv`가 GitLab 저장소에 함께 올라가는 문제가 있었다.

이를 방지하기 위해 `.gitignore`에 다음 내용을 추가했다.

```gitignore
.env
venv/
```

하지만 이미 Git에서 추적 중인 파일은 `.gitignore`에 추가하는 것만으로 제거되지 않는다는 점도 알게 되었다.

로컬의 `venv`는 유지하면서 Git에서만 제거하기 위해 다음 명령어를 사용할 수 있었다.

```bash
git rm -r --cached venv
```

이번 경험을 통해 `.gitignore`는 프로젝트를 시작하는 단계에서 미리 설정하는 것이 중요하다는 점을 배웠다.


