# 설계 결정 기록

확정된 결정과 근거. 결정 하나에 파일 하나(`NNNN-영문-제목.md`). 뒤집은 결정은 지우지 않고 상태를 「뒤집음」으로 바꿔 아래 「뒤집은 결정」 표로 옮긴다 — 되돌릴 때 근거가 필요하다.

설계의 다섯 원칙은 [PLAN](../PLAN.md) 1.3이 정본이다. 아래 결정은 모두 그 원칙의 구현이다.

번호는 유지한다. 현행 결정 Dn은 파일 00nn, 뒤집은 결정 Xn은 파일 01nn이다(제목 앞 괄호가 옛 번호이고, 문서 간 참조는 계속 Dn·Xn으로 한다). 새 결정은 다음 D 번호. 뜻이 바뀐 결정은 본문을 고친다.

## 현행 결정

| 번호 | 결정 | 상태 | 날짜 |
|---|---|---|---|
| [0001](0001-bidirectional-ko-to-ja-first.md) | (D1) 양방향 일↔한, 단 한→일을 먼저 | 채택 | — |
| [0002](0002-language-neutral-note-slots.md) | (D2) 언어 중립 노트 슬롯 중간표현 | 채택 | — |
| [0003](0003-coda-mora-table-as-transition-costs.md) | (D3) 받침↔특수모라 대응표는 격자의 전이 비용표다 | 채택 | — |
| [0004](0004-melody-template-slots-default.md) | (D4) 선율은 템플릿 슬롯이 기본, 음원 전사는 선택 층 | 채택 | — |
| [0006](0006-no-redistribution.md) | (D6) 가사·음원·선율은 재배포하지 않는다 | 채택 | — |
| [0007](0007-no-weighted-sum-pareto-front.md) | (D7) 가중합을 쓰지 않는다 — 전선과 손잡이로 대신한다 | 채택 | — |
| [0008](0008-computed-anchor-coordinates.md) | (D8) 좌표계는 계산된 앵커다 — 관찰된 한 점이 아니다 | 채택 | — |
| [0009](0009-tier-structure.md) | (D9) 티어 구조 | 채택 | — |
| [0010](0010-validate-score-with-comment-labels.md) | (D10) 발음 점수의 타당성은 댓글 라벨 + 소규모 평정으로 검증한다 | 채택 | — |
| [0011](0011-language-resources-required.md) | (D11) 언어 자원과 신경망 모델은 모두 필수 의존성 | 채택 | — |
| [0012](0012-korean-phonology-with-kiwi.md) | (D12) 한국어 음운 규칙은 형태소 경계 조건부로, Kiwi에 의존 | 채택 | — |
| [0013](0013-ipa-as-lattice-base.md) | (D13) IPA가 격자의 기반이다 | 채택 | — |
| [0014](0014-hard-constraints-by-structure.md) | (D14) 하드 제약은 비용이 아니라 구조로 금지한다 | 채택 | — |
| [0015](0015-pitch-accent-interface-only.md) | (D15) 피치 악센트는 인터페이스만 | 채택 | — |
| [0016](0016-singing-exceptions.md) | (D16) 가창 특례 — 모음 무성화와 ガ행 비음화를 적용하지 않는다 | 채택 | — |
| [0017](0017-academic-paper-path.md) | (D17) 학술 논문 경로, 지면은 미정 | 채택 | — |
| [0019](0019-n-candidates-three-values-anchor.md) | (D19) 출력은 후보 N개 + 세 값, 그리고 앵커 | 채택 | — |
| [0021](0021-llm-as-corrector-closed-loop.md) | (D21) LLM은 생성기가 아니라 교정기이고, 루프를 닫는다 | 채택 | — |
| [0022](0022-allocation-as-search-variable.md) | (D22) 배분이 탐색 변수다 — 부분 음차는 그 특수한 경우다 | 채택 | — |
| [0023](0023-tools-before-benchmark.md) | (D23) 벤치마크보다 도구를 먼저 만든다 | 채택 | — |
| [0024](0024-slot-count-as-interval.md) | (D24) 음원 없는 경로의 슬롯 수는 점이 아니라 구간이다 | 채택 | — |
| [0025](0025-segment-as-corpus-unit.md) | (D25) 코퍼스의 단위는 분절이고, 라인 대응은 의미로 정렬한다 | 채택 | — |
| [0026](0026-llm-generates-non-phonetic-spans.md) | (D26) 비음차 구간은 LLM이 생성한다 — D21을 깨지 않는다 | 채택 | — |
| [0027](0027-per-line-normalization-constant.md) | (D27) 발음 점수의 정규화 상수는 라인별이고, 무관한 실제 라인에서 추정한다 | 채택 | — |
| [0029](0029-same-model-revision.md) | (D29) 베이스라인·교정기·비음차 생성기는 같은 모델·리비전을 쓴다 | 채택 | — |
| [0030](0030-two-axes-work-coherence.md) | (D30) 축은 둘이고, 의미 축은 작품 정합성이다 | 채택 | — |
| [0031](0031-adaptation-rate-axis-and-knob.md) | (D31) 번안율은 축이자 사용자 손잡이다 | 채택 | — |
| [0032](0032-four-emission-actions.md) | (D32) 방출 행위는 네 가지다 | 채택 | — |
| [0033](0033-sino-readings-and-entering-tone.md) | (D33) 漢字 음독 대응과 入聲 운미가 대응표의 일부다 | 채택 | — |
| [0034](0034-vowel-dominant-position-weighted.md) | (D34) 발음 점수는 모음이 지배하고 위치 가중을 쓴다 | 채택 | — |
| [0035](0035-fan-covers-as-reference.md) | (D35) 레퍼런스는 공식 번안이 아니라 팬 커버다 | 채택 | — |
| [0036](0036-default-knee-of-front.md) | (D36) 기본 제시점은 전선의 무릎이다 | 채택 | — |
| [0037](0037-fixed-acceptance-exemplar.md) | (D37) 모범 사례 하나를 수용 기준으로 고정한다 | 채택 | — |
| [0038](0038-mimic-quality-floor.md) | (D38) `mimic`에는 품질 하한이 있다 — 억지 끼워맞춤 금지 | 채택 | — |
| [0039](0039-hard-constraints-genre-first-measurement.md) | (D39) 하드 제약은 제약으로 두고, 공짜는 장르에 달려 있다 — 코퍼스 5곡의 1차 측정 | 채택 | — |
| [0040](0040-segment-repetition-per-side.md) | (D40) 분절 반복은 원문 쪽과 번안 쪽을 따로 본다 | 채택 | — |
| [0041](0041-literal-vs-adaptation-data.md) | (D41) 직역과 번안을 같은 자료로 취급하지 않는다 — 그리고 "직역을 선율에 얹는 것"도 하나의 전략이다 | 채택 | — |
| [0042](0042-proper-nouns-by-target-recognition.md) | (D42) 고유명사는 목표 문화 인지도로 갈리고, 안 통하면 기능을 지켜 치환한다 | 채택 | — |

## 뒤집은 결정

| 번호 | 결정 | 상태 | 날짜 |
|---|---|---|---|
| [0101](0101-human-ranking-as-primary-metric.md) | (X1) 인간 번안 랭킹을 1차 검증 지표로 → 폐기 | 뒤집음 | — |
| [0102](0102-weighted-sum-grid-search.md) | (X2) 6성분 가중합 + 가중치 그리드 서치 → 폐기 | 뒤집음 | — |
| [0103](0103-human-evaluation-centered.md) | (X3) 사람 평가 중심 설계 → 격하 | 뒤집음 | — |
| [0104](0104-melody-length-on-estimated-slots.md) | (X4) 추정 슬롯 위에 선율 길이 제약 → 폐기 | 뒤집음 | — |
| [0105](0105-zero-dependency-core.md) | (X5) 코어 무의존성 → 폐기 | 뒤집음 | — |
| [0106](0106-lyric-hash-manual-alignment.md) | (X6) 가사 해시 커밋 + 24곡 수동 정렬 → 재조정 | 뒤집음 | — |
| [0107](0107-benchmark-as-deliverable.md) | (X7) 벤치마크·자동 지표를 산출물로 → 도구의 부품으로 격하 | 뒤집음 | — |
| [0108](0108-t0a-t0b-split.md) | (X8) T0a / T0b 분리 (구 D18) → 흡수 | 뒤집음 | — |
| [0109](0109-semantic-floor-tau.md) | (X9) 의미 하한선 τ (구 D20) → 폐기 | 뒤집음 | — |
| [0110](0110-line-level-cosine.md) | (X10) 의미 필터와 τ는 라인 단위 코사인 (구 D28) → 대체 | 뒤집음 | — |
| [0111](0111-official-adaptation-pairs.md) | (X11) 공식 번안 쌍 20~30곡 (구 D5) → 팬 커버로 교체 | 뒤집음 | — |
| [0112](0112-multi-cover-priority-rq4.md) | (X12) 같은 곡 복수 커버 우선과 RQ4(번안율 선호) (구 D35 일부 · PLAN 5절) → 범위 밖 | 뒤집음 | — |

옛 자리: 2026-11-28에 `docs/DECISIONS.md`에서 옮겼다. Dn → 00nn, Xn → 01nn. X8~X11 제목의 「구 Dxx」는 그보다 앞선 옛 번호다.
