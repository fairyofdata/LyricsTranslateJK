# tools

코퍼스 적재·집계 코드. **가사는 들어 있지 않다** — 가사가 박힌 적재 생성기는 `data/ingest/`(git 제외)에 있다.

전부 **저장소 루트에서** 실행한다. 상대 경로(`data/...`)를 쓴다.

```
python -I tools/make_metadata.py     data/metadata.csv 재생성 (커밋 대상)
python -I tools/make_reports.py      data/reports/*.md 재생성 (git 제외)
python -I tools/check_docs.py        문서 표·펜스·상호 참조 검증
python -I tools/comment_pairs.py s001  지목 댓글 라벨 → data/labels/s001_pairs.csv (커밋 대상)
```

`-I`를 쓰는 이유는 `data/` 안의 스크립트가 그 디렉터리에서 모듈을 끌어오지 않게 하려는 것이다.

| 파일 | 하는 일 |
|---|---|
| `corpus.py` | 모라·음절 계산, ja2ko 적재(`build`)와 슬롯 대조(`report`) |
| `corpus_ko2ja.py` | ko2ja 적재와 대조. 잔차 부호가 뒤집힌다 |
| `make_metadata.py` | `data/metadata.csv` 생성. **공유 음독 다리 목록이 이 파일에 손으로 들어 있다** |
| `make_reports.py` | 곡별 검수 보고서. 가사 없는 분절 요약표 + 확인 필요 분절만 본문 |
| `comment_pairs.py` | 적재본의 `comments[]`에서 어절 쌍의 모음·두음 열과 거친 일치율을 낸다. 댓글 본문·작성자는 출력하지 않는다. phon 모듈이 아니다 |
| `check_docs.py` | 문서 구조 검증. dangling `D5`·`D18`·`D20`·`D28`은 거짓 양성이다 |

절차와 함정은 `docs/HANDOFF.md`에 있다.

## 의존성

표준 라이브러리만 쓴다. `pyproject.toml`의 의존성은 아직 쓰이지 않는다 — M1에서 음운·임베딩이 들어올 때부터다.
