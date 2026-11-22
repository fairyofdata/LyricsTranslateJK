# -*- coding: utf-8 -*-
"""코퍼스 곡별 검수 보고서 (좁힌 판).

이전 판은 곡마다 원문·독음·직역·번안을 전곡 나란히 찍었다. 검수에 필요한 양보다 많았다.
이 판은 ① 분절 요약표(가사 없이 번호·행위·잔차·표시만)와 ② **확인이 필요한 분절만** 본문을
보여 준다. 정렬 오류를 짚는 데 필요한 건 다툼이 있는 구간이고, 전문은 data/lyrics/에 있다.
"""
import sys, os, json, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from corpus import morae, syl, latin_only, has_latin

OUT = "data/reports"
os.makedirs(OUT, exist_ok=True)
IDS = ["s%03d" % i for i in range(1, 13)]
SUMMARY = []

def slots(doc, s, S, T):
    """(한국어 음절, 모라, 특수모라, 예측, 잔차, 제외이유) — 방향에 맞춰 센다."""
    ko2ja = doc["direction"] == "ko2ja"
    jp, kr = (s["tgt"], s["src"]) if ko2ja else (s["src"], s["tgt"])
    JP, KR = (T, S) if ko2ja else (S, T)
    m = sp = 0; en = False
    for i in jp:
        ln = JP[i]
        if "reading_kana" in ln:
            a, b = morae(ln["reading_kana"]); m += a; sp += b
        elif latin_only(ln["text"]):
            en = True
    k = sum(syl(KR[i]["text"]) for i in kr)
    why = None
    if "repeat_of" in s:            why = "반복"
    elif s.get("slot_excluded"):    why = "정렬 미확정"
    elif not s["tgt"] or not s["src"]: why = "대응 없음"
    elif en:                        why = "영어 keep"
    elif m == 0:                    why = "독음 없음"
    elif any(has_latin(x["text"]) for i in jp + kr for x in [JP.get(i) or KR.get(i)] if x):
        why = "혼용 라인"
    if why:
        return (k, m, sp, None, None, why)
    pred = m - sp
    r = (pred - k) if ko2ja else (k - pred)
    return (k, m, sp, pred, r, None)

for sid in IDS:
    p = "data/lyrics/%s.json" % sid
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding="utf-8"))
    S = {x["id"]: x for x in d["source"]["lines"]}
    T = {x["id"]: x for x in d["target"]["lines"]}
    uniq = set(d["unique_pairs"]); pv = d["provenance"]
    ko2ja = d["direction"] == "ko2ja"
    L = []; A = L.append

    A("# %s — %s %s %s" % (sid, d["source"]["title"], "→" if ko2ja else "←", d["target"]["title"]))
    A("")
    A("> **검수용 · `git` 제외.** 확인이 필요한 분절의 가사만 싣습니다. 전문은 `data/lyrics/%s.json`에 있습니다 (D6)." % sid)
    A("")
    A("| | |"); A("|---|---|")
    A("| 원곡 | %s — %s |" % (d["source"]["title"], d["source"]["artist"]))
    A("| 번안 | %s — %s (`%s`) |" % (d["target"]["title"], d["target"]["artist"], d["target"].get("kind","?")))
    A("| 방향 | `%s` |" % d["direction"])
    if d.get("is_gold"): A("| 지위 | **모범 사례 (D37)** |")
    if pv.get("target_lyricist"): A("| 번안 작사 | %s |" % pv["target_lyricist"])
    A("")
    A("**자리매김** — %s" % d.get("note","").replace("\n"," "))
    A("")
    A("## 0. 네 가지를 섞지 않았습니다")
    A("")
    rd = "사용자 제공" if pv.get("source_reading_available") else "**분석자 생성 — 미검증**"
    gl = "사용자 제공" if pv.get("source_gloss_available") else "**분석자 생성 — 미검증**"
    A("| 칸 | 무엇 | 출처 | 슬롯 제약 |"); A("|---|---|---|---|")
    A("| 원문 | %s 가사 | 사용자 제공 | — |" % ("한국어" if ko2ja else "일본어"))
    A("| 독음 | 가나 | %s | — |" % rd)
    A("| **직역** | 원문 뜻풀이 · `gloss_ko` | %s | **없음 — 불려지지 않는다** |" % gl)
    A("| **번안** | 실제로 불려진 가사 · `target.lines` | 사용자 제공 | **있음** |")
    A("")
    A("직역은 슬롯 집계에 한 글자도 쓰지 않았습니다. 쓰는 곳은 `semantic_line` 기준값 하나뿐입니다 (D41).")
    if pv.get("gloss_note"):   A(""); A("> ⚠ %s" % pv["gloss_note"])
    if pv.get("reading_note"): A(""); A("> ⚠ %s" % pv["reading_note"])
    A("")

    rows, res, acts, flagged = [], [], collections.Counter(), []
    for s in d["segments"]:
        if s["seg_id"] not in uniq:
            continue
        obs = s.get("obs")
        if obs: acts[obs] += 1
        k, m, sp, pred, r, why = slots(d, s, S, T)
        if r is not None:
            res.append(r)
        mark = ""
        if why in ("정렬 미확정", "대응 없음", "독음 없음"):
            mark = "⚠"
        elif r is not None and abs(r) >= 2:
            mark = "⚠"
        if mark or s.get("note"):
            flagged.append((s, k, m, sp, pred, r, why, mark))
        rows.append((s["seg_id"], s["type"], obs or "", "" if r is None else "%+d" % r,
                     why or "", mark))

    A("## 1. 분절 요약 — %d개" % len(rows))
    A("")
    A("가사 없이 번호·행위·잔차만 봅니다. `잔차`는 번안이 차지하는 슬롯 − 원문이 차지하는 슬롯입니다.")
    A("")
    A("| 분절 | 꼴 | 행위 | 잔차 | 비고 | |"); A("|---|---|---|---|---|---|")
    for a, b, c, e, f, g in rows:
        A("| `%s` | %s | %s | %s | %s | %s |" % (a, b, "`%s`" % c if c else "", e, f, g))
    A("")

    A("## 2. 확인이 필요한 분절")
    A("")
    if not flagged:
        A("없습니다.")
    else:
        A("잔차가 2 이상이거나 정렬이 미확정이거나 메모를 남긴 분절입니다. **여기만 가사를 싣습니다.**")
    A("")
    for s, k, m, sp, pred, r, why, mark in flagged:
        h = "### %s · `%s`" % (s["seg_id"], s["type"])
        if s.get("obs"): h += " · `%s`" % s["obs"]
        if r is not None: h += " · 잔차 %+d" % r
        if why: h += " · %s" % why
        if mark: h += " ⚠"
        A(h); A("")
        for i in s["src"]:
            ln = S[i]; A("- **원문** %s" % ln["text"])
            if ln.get("reading_kana"):
                mm, ss = morae(ln["reading_kana"])
                A("  - 독음 `%s` — %d모라 (특수 %d)" % (ln["reading_kana"], mm, ss))
            if ln.get("gloss_ko"): A("  - 직역 %s" % ln["gloss_ko"])
        for i in s["tgt"]:
            ln = T[i]
            extra = ""
            if ln.get("reading_kana"):
                mm, ss = morae(ln["reading_kana"])
                extra = " — %d모라 (특수 %d)" % (mm, ss)
            elif not ko2ja:
                extra = " — %d음절" % syl(ln["text"])
            A("- **번안** %s%s" % (ln["text"], extra))
            if ln.get("gloss_ko"): A("  - 직역 %s" % ln["gloss_ko"])
        if not s["tgt"]: A("- **번안** _(없음)_ — %s" % s.get("reason",""))
        if pred is not None: A("- 예측 %d / 실제 %d" % (pred, k if ko2ja else k))
        if s.get("note"): A("- 메모: %s" % s["note"])
        A("")

    ex = 100*sum(1 for x in res if x == 0)/len(res) if res else 0
    w1 = 100*sum(1 for x in res if abs(x) <= 1)/len(res) if res else 0
    A("## 3. 집계"); A("")
    A("| | |"); A("|---|---|")
    A("| 원문 / 번안 줄 수 | %d / %d |" % (len(d["source"]["lines"]), len(d["target"]["lines"])))
    A("| 분절 (전체 / 분석 대상) | %d / %d |" % (len(d["segments"]), len(uniq)))
    A("| 슬롯 집계에 들어간 분절 | %d |" % len(res))
    A("| 잔차 0 | **%.0f%%** |" % ex)
    A("| \\|잔차\\|≤1 | **%.0f%%** |" % w1)
    if res: A("| 잔차 평균 / 중앙 | %+.2f / %+.1f |" % (st.mean(res), st.median(res)))
    A("| 관측 행위 | %s |" % (" · ".join("`%s` %d" % (a,b) for a,b in acts.most_common()) or "미분류"))
    A("")
    if d.get("sino_observed"):
        A("**받은 공유 음독 다리 (%d)** — %s" % (len(d["sino_observed"]), " · ".join(d["sino_observed"]))); A("")
    if d.get("sino_declined"):
        A("**있었는데 받지 않은 다리** — %s" % " · ".join(d["sino_declined"])); A("")

    A("## 4. 봐 주셔야 하는 곳"); A("")
    if pv.get("alignment_confidence"): A("- **정렬 신뢰도**: %s" % pv["alignment_confidence"])
    if not pv.get("source_reading_available"): A("- **독음을 제가 생성했습니다** — 모라 수가 검증되지 않았습니다.")
    if not pv.get("source_gloss_available"):   A("- **직역을 제가 생성했습니다** — 원문 이해가 틀렸을 수 있습니다.")
    if pv.get("normalization"): A("- 원문 정규화: %s" % pv["normalization"])
    if pv.get("storage_note"):  A("- 적재 범위: %s" % pv["storage_note"])
    nw = sum(1 for *_ , g in rows if g)
    A("- ⚠ 표시 분절 **%d개** (2절에 본문 있음)" % nw)
    A(""); A("---"); A("")
    A("생성: `scratchpad/report_gen2.py` · 원본: `data/lyrics/%s.json`" % sid)
    open(os.path.join(OUT, "%s.md" % sid), "w", encoding="utf-8").write("\n".join(L))
    SUMMARY.append((sid, d["source"]["title"], d["target"]["title"], d["direction"],
                    len(uniq), len(res), ex, w1, len(d.get("sino_observed") or []),
                    nw, d["target"].get("kind"), bool(d.get("is_gold"))))
    print("  %s.md  %s · 분절 %2d · 집계 %2d · 잔차0 %3.0f%% · |r|<=1 %3.0f%% · 다리 %2d · 확인요 %d"
          % (sid, d["direction"], len(uniq), len(res), ex, w1,
             len(d.get("sino_observed") or []), nw))

L = ["# 코퍼스 검수 보고서 — 12곡", "",
     "> **git 제외.** 확인이 필요한 분절의 가사만 싣습니다 (D6).", "",
     "각 파일은 ① 가사 없는 분절 요약표와 ② **확인이 필요한 분절만** 본문으로 보여 줍니다.",
     "전문은 `data/lyrics/<id>.json`에 있습니다. 직역은 불려지지 않으므로 슬롯 집계에 쓰지 않습니다 (D41).", "",
     "| 곡 | 원곡 → 번안 | 방향 | 분절 | 집계 | 잔차 0 | \\|r\\|≤1 | 다리 | 확인요 |",
     "|---|---|---|---|---|---|---|---|---|"]
for sid, st_, tt, dr, n, nr, ex, w1, sn, nw, kind, gold in SUMMARY:
    L.append("| [%s](%s.md)%s | %s → %s | `%s` | %d | %d | %.0f%% | %.0f%% | %d | %d |"
             % (sid, sid, " ★" if gold else "", st_[:18], tt[:18], dr, n, nr, ex, w1, sn, nw))
L += ["", "`집계` = 슬롯 대조에 들어간 분절 수. 반복·영어 `keep`·혼용 라인·정렬 미확정은 빠집니다.",
      "`확인요` = 제 정렬이 틀렸을 가능성이 있어 표시한 분절 수.", ""]
open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write("\n".join(L))
print("\ndata/reports/README.md — 12곡 인덱스")
