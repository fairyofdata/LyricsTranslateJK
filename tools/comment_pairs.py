# -*- coding: utf-8 -*-
"""지목 댓글 라벨 → 어절 쌍의 추상 특징 (SPEC 11.4).

입력  data/lyrics/<sid>.json 의 comments[]  (git 제외 — 댓글 본문이 들어 있다)
출력  data/labels/<sid>_pairs.csv          (커밋 대상 — 어절 쌍·모음/자음 열·일치율·지지 댓글 수만)

이건 phon 모듈이 아니다. 모음 5~7부류 · 두음 9부류의 거친 일치율로, 「사람이 받아들인
대응에서 모음과 자음 중 어느 쪽이 더 겹치는가」(D34)를 먼저 보려는 것이다.
"""
import sys, os, json, csv
sys.stdout.reconfigure(encoding="utf-8")

# ---------- 일본어: 가나 → 음절(특수모라·장음은 앞 음절에 흡수) ----------
ROWS = {"": "あいうえお", "K": "かきくけこがぎぐげご", "S": "さしすせそ", "C": "ざじずぜぞぢづ",
        "T": "たてとだでど", "N": "なにぬねの", "H": "はひふへほ", "P": "ばびぶべぼぱぴぷぺぽ",
        "M": "まみむめも", "Y": "やゆよ", "R": "らりるれろ", "W": "わを"}
VOW = {}
for row in ["あいうえお", "かきくけこ", "さしすせそ", "たちつてと", "なにぬねの", "はひふへほ",
            "まみむめも", "らりるれろ", "がぎぐげご", "ざじずぜぞ", "だぢづでど", "ばびぶべぼ", "ぱぴぷぺぽ"]:
    for k, v in zip(row, "aiueo"):
        VOW[k] = v
VOW.update({"や": "a", "ゆ": "u", "よ": "o", "わ": "a", "を": "o"})
ONS = {k: c for c, ks in ROWS.items() for k in ks}
ONS.update({"ち": "C", "つ": "C"})
SMALLV = {"ゃ": "a", "ゅ": "u", "ょ": "o", "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o"}

def hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)

def ja_syllables(kana):
    out = []                                   # [(onset, vowel)]
    for c in hira(kana):
        if c in " 　":
            continue
        if c in SMALLV and out:
            out[-1] = (out[-1][0], SMALLV[c]); continue
        if c in "んっー" and out:
            continue                           # 앞 음절에 흡수 (SPEC 1.2 extend)
        if out and ((c == "う" and out[-1][1] in "ou") or (c == "い" and out[-1][1] == "e")):
            continue                           # 장음 표기
        if c in VOW:
            out.append((ONS.get(c, ""), VOW[c]))
    return out

# ---------- 한국어: 음절 → (두음, 핵모음) ----------
CHO = ["K", "K", "N", "T", "T", "R", "M", "P", "P", "S", "S", "", "C", "C", "C", "K", "T", "P", "H"]
JUNG = ["a", "e", "a", "e", "ʌ", "e", "ʌ", "e", "o", "a", "e", "e", "o", "u", "ʌ", "e", "i", "u", "ɯ", "i", "i"]

def ko_syllables(s):
    out = []
    for ch in s:
        o = ord(ch) - 0xAC00
        if 0 <= o < 11172:
            out.append((CHO[o // 588], JUNG[(o % 588) // 28]))
    return out

def v_eq(a, b):
    return a == b or {a, b} == {"u", "ɯ"}     # 일본어 う는 [ɯ]

def align(x, y):
    """모음 일치를 최대화하는 단조 정렬 (Needleman–Wunsch). 짝지어진 (i, j) 목록."""
    n, m = len(x), len(y)
    S = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): S[i][0] = -i
    for j in range(1, m + 1): S[0][j] = -j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            S[i][j] = max(S[i-1][j-1] + (1 if v_eq(x[i-1][1], y[j-1][1]) else 0),
                          S[i-1][j] - 1, S[i][j-1] - 1)
    i, j, pairs = n, m, []
    while i > 0 and j > 0:
        if S[i][j] == S[i-1][j-1] + (1 if v_eq(x[i-1][1], y[j-1][1]) else 0):
            pairs.append((i-1, j-1)); i -= 1; j -= 1
        elif S[i][j] == S[i-1][j] - 1: i -= 1
        else: j -= 1
    return pairs[::-1]

def main(sid):
    d = json.load(open("data/lyrics/%s.json" % sid, encoding="utf-8"))
    T = {x["id"]: x for x in d["target"]["lines"]}
    G = {g["seg_id"]: g for g in d["segments"]}
    rows = []
    for c in d.get("comments", []):
        if c["kind"] != "sound":
            rows.append(dict(song_id=sid, seg_id=c["seg_id"], kind=c["kind"], pair_src=c["pair_src"],
                             pair_tgt=c["pair_tgt"], n_comments=len(c["comment_ns"])))
            continue
        js, ks = ja_syllables(c["pair_src_kana"]), ko_syllables(c["pair_tgt"])
        pr = align(js, ks)
        vm = sum(v_eq(js[i][1], ks[j][1]) for i, j in pr)
        om = sum(js[i][0] == ks[j][0] for i, j in pr)
        tline = " ".join(T[k]["text"] for k in G[c["seg_id"]]["tgt"]).replace(" ", "")
        rows.append(dict(
            song_id=sid, seg_id=c["seg_id"], kind="sound", pair_src=c["pair_src"], pair_tgt=c["pair_tgt"],
            src_syll=len(js), tgt_syll=len(ks), aligned=len(pr),
            src_vowels="-".join(v for _, v in js), tgt_vowels="-".join(v for _, v in ks),
            src_onsets="-".join(o or "∅" for o, _ in js), tgt_onsets="-".join(o or "∅" for o, _ in ks),
            vowel_match="%.2f" % (vm / len(pr)) if pr else "", onset_match="%.2f" % (om / len(pr)) if pr else "",
            line_final=str(tline.endswith(c["pair_tgt"].replace(" ", ""))).lower(),
            n_comments=len(c["comment_ns"])))
    os.makedirs("data/labels", exist_ok=True)
    cols = ["song_id", "seg_id", "kind", "pair_src", "pair_tgt", "src_syll", "tgt_syll", "aligned",
            "src_vowels", "tgt_vowels", "src_onsets", "tgt_onsets", "vowel_match", "onset_match",
            "line_final", "n_comments"]
    with open("data/labels/%s_pairs.csv" % sid, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    snd = [r for r in rows if r["kind"] == "sound"]
    for r in snd:
        print("%-10s %-14s %-12s V %s | %-13s C %s | %-13s %s" % (
            r["seg_id"], r["pair_src"], r["pair_tgt"], r["vowel_match"], r["src_vowels"] + "/" + r["tgt_vowels"],
            r["onset_match"], r["src_onsets"] + "/" + r["tgt_onsets"], "끝" if r["line_final"] == "true" else ""))
    tv = sum(float(r["vowel_match"]) * r["aligned"] for r in snd); to = sum(float(r["onset_match"]) * r["aligned"] for r in snd)
    n = sum(r["aligned"] for r in snd)
    print("\n소리 쌍 %d개 · 짝지은 음절 %d · 모음 일치 %.0f%% · 두음 일치 %.0f%%" % (len(snd), n, 100 * tv / n, 100 * to / n))
    print("data/labels/%s_pairs.csv — %d행" % (sid, len(rows)))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "s001")
