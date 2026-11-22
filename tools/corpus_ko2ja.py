# -*- coding: utf-8 -*-
"""ko2ja 적재 — 원문이 한국어, 번안이 일본어. 집계 방향이 뒤집힌다.

잔차 정의는 ja2ko와 같게 유지한다:  잔차 = (번안이 차지하는 슬롯) - (원문이 차지하는 슬롯)
ja2ko:  잔차 = 한국어 음절 - (모라 - 특수모라)
ko2ja:  잔차 = (모라 - 특수모라) - 한국어 음절
"""
import sys, os, json, hashlib, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from corpus import morae, syl, latin_only, has_latin

def build_ko2ja(song_id, cover_id, note, src_meta, tgt_meta, src, tgt, segspec, prov):
    """src = [(section, 한국어 가사)]  ·  tgt = [(section, 일본어 가사, 가나, 직역)]"""
    src_lines = [{"id": "K%02d" % i, "section": s, "text": t}
                 for i, (s, t) in enumerate(src, 1)]
    tgt_lines = []
    for i, row in enumerate(tgt, 1):
        sec, txt, kana, gloss = row
        d = {"id": "J%02d" % i, "section": sec, "text": txt}
        if kana:  d["reading_kana"] = kana
        if gloss: d["gloss_ko"] = gloss
        tgt_lines.append(d)
    segs = []
    for n, si, ti, extra in segspec:
        d = {"seg_id": "%s-g%02d" % (song_id, n),
             "src": ["K%02d" % x for x in si],
             "tgt": ["J%02d" % x for x in ti],
             "type": "%d:%d" % (len(si), len(ti))}
        d.update(extra)
        segs.append(d)
    uniq = [s["seg_id"] for s in segs if "repeat_of" not in s]
    doc = {"song_id": song_id, "cover_id": cover_id, "direction": "ko2ja", "note": note,
           "source": dict(src_meta, lines=src_lines),
           "target": dict(tgt_meta, lines=tgt_lines),
           "segments": segs, "unique_pairs": uniq, "provenance": prov}
    os.makedirs("data/lyrics", exist_ok=True)
    with open("data/lyrics/%s.json" % song_id, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return doc

def report_ko2ja(doc):
    S = {d["id"]: d for d in doc["source"]["lines"]}
    T = {d["id"]: d for d in doc["target"]["lines"]}
    uniq = set(doc["unique_pairs"])
    res = []
    print("\n=== %s  %s → %s  (ko2ja) ===" % (doc["song_id"], doc["source"]["title"],
                                              doc["target"]["title"]))
    print("%-11s %-5s %5s %5s %5s %5s %6s  %s"
          % ("seg", "type", "ko", "mora", "sp", "pred", "resid", "원문(한국어)"))
    for s in doc["segments"]:
        if s["seg_id"] not in uniq:
            continue
        k = sum(syl(S[i]["text"]) for i in s["src"])
        m = sp = 0; en = False
        for i in s["tgt"]:
            ln = T[i]
            if "reading_kana" in ln:
                a, b = morae(ln["reading_kana"]); m += a; sp += b
            elif latin_only(ln["text"]):
                en = True
        bad = (s.get("slot_excluded") or not s["tgt"] or en or m == 0
               or any(has_latin(T[i]["text"]) for i in s["tgt"])
               or any(has_latin(S[i]["text"]) for i in s["src"]))
        if bad:
            print("%-11s %-5s %s" % (s["seg_id"], s["type"], "[슬롯 집계 제외]"))
            continue
        pred = m - sp
        res.append(pred - k)
        print("%-11s %-5s %5d %5d %5d %5d %+6d  %s"
              % (s["seg_id"], s["type"], k, m, sp, pred, pred - k,
                 " / ".join(S[i]["text"] for i in s["src"])[:28]))
    if res:
        print("  분절 %d · 잔차 평균 %+.2f · 중앙 %+.1f · =0 %.0f%% · |r|<=1 %.0f%% · |r|<=2 %.0f%%"
              % (len(res), st.mean(res), st.median(res),
                 100*sum(1 for x in res if x == 0)/len(res),
                 100*sum(1 for x in res if abs(x) <= 1)/len(res),
                 100*sum(1 for x in res if abs(x) <= 2)/len(res)))
    srct = "\n".join(d["text"] for d in doc["source"]["lines"])
    tgtt = "\n".join(d["text"] for d in doc["target"]["lines"])
    print("  src_sha256 %s" % hashlib.sha256(srct.encode()).hexdigest())
    print("  tgt_sha256 %s" % hashlib.sha256(tgtt.encode()).hexdigest())
    print("  ko_syl_total %d · lines %d/%d · segments %d (unique %d)"
          % (sum(syl(d["text"]) for d in doc["source"]["lines"]),
             len(doc["source"]["lines"]), len(doc["target"]["lines"]),
             len(doc["segments"]), len(doc["unique_pairs"])))
    return res
