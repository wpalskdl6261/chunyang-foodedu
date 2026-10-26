# 춘양초 식생활교육

학교급식 선도학교를 운영하는 춘양초등학교의 식생활교육 홍보 페이지입니다.
오늘의 급식, 식생활교육 일곱 갈래 소개, 월별 교육 인포그래픽, 보도자료(봉화교육지원청 학교교육홍보)를 한 페이지에 담았습니다.

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `index.html` | 공개되는 페이지 (`tools/build.py`로 만든 결과물, 직접 고치지 않기) |
| `src/index.src.html` | 페이지 원본 (화면 구성, 스타일, 스크립트) |
| `content/press/*.json` | 보도자료 한 건씩 (제목, 날짜, 본문, 사진, 원문 링크) |
| `content/press-themes.json` | 보도자료별 갈래와 월별 표에 쓰는 짧은 이름 |
| `assets/` | 교표, 보도자료 사진 (긴 변 800px로 줄인 것) |
| `tools/` | 페이지 만들기·보도자료 가져오기 도구, Pretendard 글꼴 |

## 페이지 만들기

Python 3.9 이상이 필요합니다.

```bash
python tools/build.py
```

`src/` 또는 `content/`를 고친 뒤 위 명령으로 `index.html`을 다시 만듭니다.
`python tools/build.py --single`은 글꼴과 사진을 모두 안에 넣은 한 파일(`dist/chunyang-food-edu.html`)을 만듭니다.

## 보도자료 추가하기

봉화교육지원청 학교교육홍보 게시글 주소 끝의 `nttSn` 번호로 가져옵니다. 사진을 줄이는 데 Pillow가 필요합니다(`pip install pillow`).

```bash
python tools/scrape.py .cache/pages .cache/drafts 1651179
python tools/import_press.py .cache/drafts .cache/press-raw assets/press content/press
```

그다음 `content/press-themes.json`에 새 게시글 번호의 갈래(`rice`, `culture`, `green`, `student`, `app`, `community`, `career`)와 짧은 이름을 넣고 페이지를 다시 만듭니다.

## 자료실에 자료 넣기

`content/library.json`에 한 줄씩 추가하고 파일은 `assets/library/` 아래에 둡니다.

- 영상: `videos`에 `{"id", "title", "date", "duration", "src" 또는 "youtube"(영상 ID), "poster", "desc"}`
- 월별 영양교육자료: `monthly`에 `{"month": "2026-11", "topic", "grade", "file"}`
- 사업 결과 보고서: `reports`의 해당 사업 `items`에 `{"title", "date", "file", "pages", "cover", "grade"(학년별 프로젝트일 때)}`

## GitHub Pages로 공개하기

저장소의 **Settings → Pages**에서 Source를 `Deploy from a branch`, Branch를 `main` / `(root)`로 정하면
`https://<아이디>.github.io/<저장소 이름>/` 주소로 공개됩니다.

## 출처와 라이선스

- 보도자료 본문과 사진: 경상북도봉화교육지원청 학교교육홍보 게시판 (춘양초등학교 작성)
- 글꼴: [Pretendard](https://github.com/orioncactus/pretendard) 1.3.9, SIL Open Font License 1.1 (`tools/fonts/LICENSE.txt`)
