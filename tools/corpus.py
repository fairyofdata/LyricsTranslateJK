# -*- coding: utf-8 -*-
"""s002~s004 적재 + 슬롯 대조. 프로젝트 루트에서 실행."""
import json, sys, os, hashlib, statistics as st
sys.stdout.reconfigure(encoding="utf-8")

# ---------------- 모라 / 음절 계산 ----------------
SMALL = set("ゃゅょぁぃぅぇぉャュョァィゥェォ")
SPECIAL = set("んンっッー")
ROW_V = {}
for row in ["あいうえお","かきくけこ","さしすせそ","たちつてと","なにぬねの",
            "はひふへほ","まみむめも","やいゆえよ","らりるれろ","わいうえお",
            "がぎぐげご","ざじずぜぞ","だぢづでど","ばびぶべぼ","ぱぴぷぺぽ",
            "アイウエオ","カキクケコ","サシスセソ","タチツテト","ナニヌネノ",
            "ハヒフヘホ","マミムメモ","ヤイユエヨ","ラリルレロ","ワイウエオ",
            "ガギグゲゴ","ザジズゼゾ","ダヂヅデド","バビブベボ","パピプペポ"]:
    for k, v in zip(row, "aiueo"):
        ROW_V[k] = v

def morae(kana):
    """(모라 수, 특수모라 수). 특수모라 = ん·っ·ー + 장음 표기(おう·ゅう·えい)."""
    if not kana:
        return (0, 0)
    units = []
    for ch in kana:
        if ch in " 　、。!?！？、。":
            continue
        if ch in SMALL and units:
            units[-1] = units[-1] + ch
            continue
        units.append(ch)
    sp = 0
    for i, u in enumerate(units):
        c = u[0]
        if c in SPECIAL:
            sp += 1
            continue
        if i == 0:
            continue
        p = units[i - 1]
        last = p[-1]
        if last in "ゃャ":   pv = "a"
        elif last in "ゅュ": pv = "u"
        elif last in "ょョ": pv = "o"
        else:               pv = ROW_V.get(last)
        if c in "うウ" and pv in ("o", "u"):
            sp += 1
        elif c in "いイ" and pv == "e":
            sp += 1
    return (len(units), sp)

def syl(s):
    return sum(1 for ch in s if 0xAC00 <= ord(ch) <= 0xD7A3)

def has_latin(s):
    return bool(__import__('re').search(r'[A-Za-z]', s))

def latin_only(s):
    return not any(0x3040 <= ord(c) <= 0x30FF or 0x4E00 <= ord(c) <= 0x9FFF
                   or 0xAC00 <= ord(c) <= 0xD7A3 for c in s)

# ---------------- 공통 적재 루틴 ----------------
def build(song_id, cover_id, direction, note, src_meta, tgt_meta,
          src, tgt, segspec, prov):
    src_lines = []
    for i, row in enumerate(src, 1):
        sec, txt, kana, gloss = row
        d = {"id": "J%02d" % i, "section": sec, "text": txt}
        if kana:  d["reading_kana"] = kana
        if gloss: d["gloss_ko"] = gloss
        src_lines.append(d)
    tgt_lines = [{"id": "K%02d" % i, "section": s, "text": t}
                 for i, (s, t) in enumerate(tgt, 1)]
    segs = []
    for n, si, ti, extra in segspec:
        d = {"seg_id": "%s-g%02d" % (song_id, n),
             "src": ["J%02d" % x for x in si],
             "tgt": ["K%02d" % x for x in ti],
             "type": "%d:%d" % (len(si), len(ti))}
        d.update(extra)
        segs.append(d)
    uniq = [s["seg_id"] for s in segs if "repeat_of" not in s]
    doc = {"song_id": song_id, "cover_id": cover_id, "direction": direction,
           "note": note,
           "source": dict(src_meta, lines=src_lines),
           "target": dict(tgt_meta, lines=tgt_lines),
           "segments": segs, "unique_pairs": uniq, "provenance": prov}
    os.makedirs("data/lyrics", exist_ok=True)
    with open("data/lyrics/%s.json" % song_id, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return doc

def report(doc):
    S = {d["id"]: d for d in doc["source"]["lines"]}
    T = {d["id"]: d for d in doc["target"]["lines"]}
    uniq = set(doc["unique_pairs"])
    rows = []
    print("\n=== %s  %s ← %s ===" % (doc["song_id"], doc["target"]["title"],
                                     doc["source"]["title"]))
    print("%-11s %-5s %5s %5s %5s %5s %6s  %s"
          % ("seg", "type", "mora", "sp", "pred", "ko", "resid", "원문"))
    for s in doc["segments"]:
        if s["seg_id"] not in uniq:
            continue
        if (s.get("slot_excluded") or s["type"].endswith(":0")
                or any(has_latin(T[i]["text"]) for i in s["tgt"])):
            print("%-11s %-5s %s" % (s["seg_id"], s["type"], "[슬롯 집계 제외]"))
            continue
        m = sp = 0
        skip = False
        for i in s["src"]:
            ln = S[i]
            if "reading_kana" in ln:
                a, b = morae(ln["reading_kana"]); m += a; sp += b
            elif latin_only(ln["text"]):
                skip = True
        k = sum(syl(T[i]["text"]) for i in s["tgt"])
        if skip:
            print("%-11s %-5s %s" % (s["seg_id"], s["type"], "[영어 keep — 집계 제외]"))
            continue
        pred = m - sp
        rows.append(k - pred)
        print("%-11s %-5s %5d %5d %5d %5d %+6d  %s"
              % (s["seg_id"], s["type"], m, sp, pred, k, k - pred,
                 " / ".join(S[i]["text"] for i in s["src"])[:30]))
    if rows:
        print("  분절 %d · 잔차 평균 %+.2f · 중앙 %+.1f · =0 %.0f%% · |r|<=1 %.0f%% · |r|<=2 %.0f%%"
              % (len(rows), st.mean(rows), st.median(rows),
                 100 * sum(1 for x in rows if x == 0) / len(rows),
                 100 * sum(1 for x in rows if abs(x) <= 1) / len(rows),
                 100 * sum(1 for x in rows if abs(x) <= 2) / len(rows)))
    srct = "\n".join(d["text"] for d in doc["source"]["lines"])
    tgtt = "\n".join(d["text"] for d in doc["target"]["lines"])
    print("  src_sha256 %s" % hashlib.sha256(srct.encode()).hexdigest())
    print("  tgt_sha256 %s" % hashlib.sha256(tgtt.encode()).hexdigest())
    print("  ko_syl_total %d · lines %d/%d · segments %d (unique %d, 1:0 %d)"
          % (sum(syl(d["text"]) for d in doc["target"]["lines"]),
             len(doc["source"]["lines"]), len(doc["target"]["lines"]),
             len(doc["segments"]), len(doc["unique_pairs"]),
             sum(1 for s in doc["segments"] if s["type"].endswith(":0"))))
    return rows
