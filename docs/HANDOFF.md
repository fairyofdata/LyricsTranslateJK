# 인계 문서

다음 세션이 이 작업을 이어받는 데 필요한 것만 적는다. **지금 상태는 여기 쓰지 않는다** — 상태는 `state.md` 하나에만 있다(git 제외, `CLAUDE.local.md`가 매 세션 읽어 온다). 이 문서는 **구조와 절차**다.

## 1. 읽는 순서

| | |
|---|---|
| 1 | `state.md` — 지금 어디까지 왔는가 (자동으로 읽힌다) |
| 2 | `docs/DIGEST.md` — 한 장 요약. 우선순위·상수·미검증 가정 |
| 3 | `docs/DECISIONS.md` — 현행 결정 D1~D42, 뒤집은 결정 X1~X11 |
| 4 | 이 문서 — 코퍼스를 만지거나 늘릴 때 |
| 5 | `docs/SPEC.md` · `docs/PLAN.md` — 세부 사양과 계획 |

설계 질문의 정본은 `DIGEST`·`DECISIONS`다. 어긋나면 그쪽이 맞다.

## 2. 무엇이 커밋되고 무엇이 로컬인가

가사·음원·선율·댓글 본문은 재배포하지 않는다(D6). 저장소는 **공개**다.

```
커밋됨
  README.md  docs/            기획·사양·결정·인계
  tools/                      분석 코드 (가사 없음)
  data/metadata.csv           곡별 해시·집계값만
  data/labels/<id>_pairs.csv  지목 댓글 라벨 — 어절 쌍·모음/자음 열·지지 댓글 수 (본문·작성자 없음)
  data/candidates.md          공식 번안 조사 (가사 본문 없음)
  pyproject.toml  .gitignore

git 제외 (이 PC에만)
  state.md  CLAUDE.local.md   지금 상태
  data/lyrics/<id>.json       적재본 — 가사 전문이 들어 있다
  data/ingest/run*.py         적재 생성기 — 가사가 소스에 박혀 있다
  data/reports/<id>.md        검수 보고서 — 확인 필요 분절의 가사
  data/comments/<id>_raw.txt  댓글 원본 (사용자 붙여넣기) — 작성자명·본문
```

**커밋 전에 `data/`를 매번 확인한다.** `git status --short`에 `data/lyrics`·`data/ingest`·`data/reports`가 뜨면 `.gitignore`가 깨진 것이다.

## 3. 코퍼스

14곡. 목록·수치는 `state.md`와 `data/metadata.csv`에, 곡별 분절 대조는 `data/reports/<id>.md`에 있다.

적재본은 `data/lyrics/<id>.json` 하나가 정본이고, `data/ingest/run<id>.py`가 그것을 만든 생성기다. 생성기를 다시 돌리면 같은 JSON이 나온다 — 해시로 확인했다.

**예외 하나: `s002`에는 생성기가 없다.** 번호 정정(에바 번안이 1번) 전에 인라인 스크립트로 적재했고 그 스크립트는 남지 않았다. `data/lyrics/s002.json`이 유일한 원본이므로 **지우면 복구할 수 없다.** 다시 만들려면 사용자에게 원문을 다시 받아야 한다.

### 적재 JSON의 모양

정본 정의는 `SPEC 10.3`이다. 요점만:

- `source` = 원곡, `target` = 실제로 불려진 번안. **방향과 무관하게 이 뜻이다** (ko2ja면 `source`가 한국어다)
- `source.lines[].gloss_ko` = **직역**. 불려지지 않으므로 슬롯 집계에 한 글자도 쓰지 않는다 (D41)
- `segments[].obs` = 내가 손으로 판정한 관측 행위(`keep`/`sino`/`mimic`/`render`). 없는 분절은 미분류다
- `repeat_of`는 **양쪽이 모두 반복일 때만** 쓰고 그때만 `unique_pairs`에서 뺀다. 한쪽만이면 `src_repeat_of`/`tgt_repeat_of`이고 분석에 남는다 (D40)
- `slot_excluded: true` = 슬롯 집계에서 뺀다. 정렬 미확정·축약 전사·`keep` 등
- `segments[].obs_parts` = 한 분절 안의 어절 단위 행위 목록. `obs`는 그중 대표 하나다
- `target.lines[].listed_text` = 설명란 표기가 **불린 것과 다를 때** 설명란 쪽. `sung_as: "ja"`면 원어로 불렸다
- `comments[]` = 지목 댓글 라벨. `comment_ns`는 `data/comments/`의 구조화 번호다

## 4. 절차 — 곡 하나 늘리기

수집은 사용자, 적재·분석은 분석자다. 붙여넣을 형식은 `docs/INTAKE.md`.

```
1. data/ingest/run<id>.py 를 쓴다        기존 것을 복사해 가사와 분절만 바꾼다
2. python -I data/ingest/run<id>.py      JSON 생성 + 슬롯 대조 출력
3. tools/make_metadata.py 의 SINO·DECLINED·META 에 그 곡을 추가한다
4. python -I tools/make_metadata.py      data/metadata.csv 재생성
5. python -I tools/make_reports.py       data/reports/*.md 재생성
6. 설계에 반영할 것이 있으면 DECISIONS·SPEC·DIGEST, 그리고 state.md
```

모두 **저장소 루트에서** 실행한다(상대 경로를 쓴다). `python -I`로 돌린다 — `data/` 안의 스크립트가 그 디렉터리에서 모듈을 끌어오지 않게 한다.

### tools/

| 파일 | 하는 일 |
|---|---|
| `corpus.py` | 모라·음절 계산, ja2ko 적재(`build`)와 슬롯 대조(`report`) |
| `corpus_ko2ja.py` | ko2ja 적재와 대조. **잔차 부호가 뒤집힌다** |
| `make_metadata.py` | `data/metadata.csv` 생성. 공유 음독 다리 목록이 여기 손으로 들어 있다 |
| `make_reports.py` | `data/reports/*.md` 생성. 양방향 처리 |
| `check_docs.py` | 문서의 표·펜스·상호 참조 검증 |
| `comment_pairs.py` | 적재본의 `comments[]` → `data/labels/<id>_pairs.csv`. 모음·두음 거친 일치율 (phon 모듈이 아니다) |

`check_docs.py`의 dangling `D5`·`D18`·`D20`·`D28`은 **거짓 양성**이다 — `X8`~`X11` 제목의 "구 Dxx" 과거 번호 표기이고 `DECISIONS` 머리의 규칙대로 의도된 것이다. 그 넷 외에 뜨면 실제 문제다.

### 잔차의 정의

```
잔차 = 번안이 차지하는 슬롯 − 원문이 차지하는 슬롯
예측 = 모라 수 − 특수모라 수            특수모라 = ん · っ · ー · 장음 표기
ja2ko:  잔차 = 한국어 음절 − 예측
ko2ja:  잔차 = 예측 − 한국어 음절
```

한·영 혼용 라인과 영어 전용 라인은 한글 음절만 세면 과소 집계되므로 **자동으로 집계에서 빠진다.**

## 5. 빠지기 쉬운 함정

이 세션에서 실제로 빠졌던 것들이다.

- **`grep`의 유니코드 문자 범위를 믿지 마라.** `grep -c '[ぁ-んァ-ヶ]'`은 UTF-8을 모르고 바이트로 매칭해서 한글까지 센다. 문자 종류를 셀 일은 파이썬 코드포인트 범위로 한다
- **문서 패치는 줄바꿈을 정규화하고 해야 한다.** `README.md`·`docs/DIGEST.md`는 LF, 나머지 문서는 CRLF다. 여러 줄 앵커가 조용히 안 걸린다. 읽을 때 `\r\n`→`\n`으로 바꾸고 쓸 때 되돌린다
- **백틱이 든 내용을 bash 인라인으로 쓰지 마라.** 명령 치환으로 먹힌다. 따옴표 heredoc(`<< 'PYEOF'`)이나 파일로 쓴다. 파이썬 문자열 안의 `\\`도 heredoc을 한 번 더 지난다
- **방향을 타는 집계는 양쪽을 다 시험한다.** `make_metadata.py`가 한동안 ko2ja를 ja2ko 공식으로 세서 `metadata.csv`의 일치율이 1.00으로 들어가 있었다. 커밋 대상 파일이라 조용히 틀리면 오래 남는다
- **곡 번호를 바꿨으면 생성기도 고친다.** `run002.py`가 번호 정정 전 `song_id`를 들고 있어서 다시 돌리면 다른 곡을 덮어쓸 상태였다
- **설명란 가사가 불린 가사라고 믿지 마라.** `s001`의 설명란은 원어 그대로 부른 후렴 두 구절 자리에 한국어 뜻풀이를 적어 두었고, 그걸 번안으로 읽어 `keep`을 `sino`로 잘못 판정했다 — 다리 수가 두 배로 부풀었다. 사용자가 처음부터 "원어 그대로"라고 말했고 댓글도 그랬다. 직역과 번안이 겹치면(D41 점검) 먼저 의심한다
- **사용자가 짚은 것은 적재 메모에 남긴다.** 위 착오는 사용자 설명이 적재본까지 오지 않아서 생겼다
- **보고서는 필요한 만큼만 찍는다.** 처음엔 곡마다 원문·독음·직역·번안을 전곡 나란히 찍었는데, 검수에 필요한 건 다툼이 있는 분절이고 나머지는 상업 음원의 전문 사본을 한 벌 더 만드는 셈이었다. 지금은 가사 없는 요약표 + 확인 필요 분절만이다

## 6. 다음에 할 일

순서와 완료 조건은 `state.md`의 「다음 작업」이 정본이다. 코퍼스 쪽으로 가장 급한 것만 적는다. 같은 곡 복수 커버는 모으지 않는다(X12).

| | 왜 |
|---|---|
| **지목 댓글을 더 모으기** | `s001` 채굴 완료(2026-11-23) — 소리 쌍 7·keep 2. 7쌍으로는 `phon` 모수를 못 맞춘다. 다른 팬 커버의 댓글이 필요하다 (D10·D34·D38) |
| **ko2ja 더 모으기** | 2곡. D1이 한→일을 먼저 완성한다 |

코드를 쓰기 시작할 시점은 `PLAN 8`의 M1이고, **구현 착수는 사용자 승인 사항이다.** 지금까지는 기획과 코퍼스뿐이다.
