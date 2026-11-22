# -*- coding: utf-8 -*-
"""s001~s005 횡단 집계 + data/metadata.csv 재작성."""
import sys, os, json, csv, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from corpus import morae, syl, latin_only, has_latin

SINO = {
 "s001": ["残酷/잔혹","天使/천사","テーゼ/테제","運命/운명","未来/미래",
          "少年/소년","神話/신화","意味/의미","自由/자유","歴史/역사"],
 "s002": ["未来/미래","ライン/라인"],
 "s003": ["季節/계절","記憶/기억"],
 "s004": [],
 "s005": [],
 "s006": ["時計/시계","八月/8월","運命/운명","未来/미래","世界/세계","義務/의무"],
 "s007": ["心臓/심장","意味/의미","記憶/기억"],
 "s008": [],
 "s009": ["退化/퇴화","電気/전기","未来/미래","弱点/약점","未知/미지","遭遇/조우","地球/지구",
          "経験値/경험치","上昇/상승","中/중","奇跡/기적","主人公/주인공","冒険/모험"],
 "s010": ["遅刻/지각","時間/시간","応援/응원","中/중","才能/재능","世界/세계","征服/정복",
          "無限/무한","絶対/절대","宇宙/우주","地球/지구","中心/중심"],
 "s011": ["시간/時間","세계/世界","축제/祝祭"],
 "s012": ["현실/現実","영원/永遠","마법/魔法","우주/宇宙","시계/時計","금지/禁止","주문/呪文","계단/階段"],
}
DECLINED = {
 "s001": ["バイブル/바이블 — 번안이 버렸다"],
 "s002": [],
 "s003": ["季節/계절 — chorus3에서 다리를 받지 않고 '먼 길의 끝'으로 갔다"],
 "s004": ["彗星/혜성 — 원문이 和語 복합어 ほうき星라 다리가 애초에 없다"],
 "s005": [],
 "s006": ["万華鏡/만화경 — 한국어 레지스터가 생경하다","教科書/교과서 — 같은 이유","権利/권리 — 선택으로 바꿨다","辞書/사서 — 한국어에서 사어라 사전(辭典)으로 갔다"],
 "s007": ["時/시간 — 단일 漢字는 한국어 자립어가 아니라 복합어로 늘려야 한다. 1漢字=1음절이 깨진다"],
 "s008": ["曖昧/애매 — 닿을 수 없는·달콤 씁쓸한으로 갔다","最初/최초 — 처음으로 갔다","鼓動/고동 — 심장 소리·가슴으로 갔다"],
 "s009": ["命中/명중 — 백발백중으로 늘려 길이를 맞췄다","困難/곤란 — 시련으로 갔다","天才·最大 — 완전 최고로","球体/구체 — 동글이로 (장치 재구성)"],
 "s010": ["失敗/실패 — 실수로 갔다","長所·短所 — 한국어는 長點·短點이라 복합어가 다르다","成層圏/성층권 — 대기권으로","銀河/은하 — 화성으로 규모를 줄였다","小野小町 — 아프로디테로 문화적 치환 (D42)"],
 "s011": ["영원/永遠 — 글자는 맞췄는데 とわ로 읽어 소리 다리가 끊겼다 (읽기 선택)","신기루 — mirage로, 제3언어로 갔다"],
 "s012": ["열차/列車 — 일본어가 汽車를 골랐다","세상/世上 — 世界로 다른 복합어","교실/教室 — 部屋으로","꼬리별 — 고유어인데 번안이 彗星을 끌어왔다 (역방향)"],
}
META = {
 "s001": dict(cover_channel="도비비 DovIvI", cover_url="https://www.youtube.com/watch?v=pLSHaE-A8z8"),
 "s002": dict(cover_channel="10CM", cover_url=""),
 "s003": dict(cover_channel="DK(디셈버)", cover_url=""),
 "s004": dict(cover_channel="윤하", cover_url=""),
 "s005": dict(cover_channel="큐빅(Q Big)", cover_url=""),
 "s006": dict(cover_channel="로이킴", cover_url=""),
 "s007": dict(cover_channel="송소희", cover_url=""),
 "s008": dict(cover_channel="冨岡愛 (TOMIOKA AI)", cover_url=""),
 "s009": dict(cover_channel="CUTIE STREET", cover_url=""),
 "s010": dict(cover_channel="CUTIE STREET", cover_url=""),
 "s011": dict(cover_channel="IZ*ONE", cover_url=""),
 "s012": dict(cover_channel="투모로우바이투게더", cover_url=""),
}
import hashlib
rows = []
print("%-6s %-24s %5s %5s %6s %6s %6s %6s  %s"
      % ("id","번안 제목","분절","슬롯","잔차0","|r|<=1","sino","keep","관측 행위 분포"))
for sid in ["s001","s002","s003","s004","s005","s006","s007","s008","s009","s010","s011","s012"]:
    p = "data/lyrics/%s.json" % sid
    if not os.path.exists(p):
        print(sid, "없음"); continue
    d = json.load(open(p, encoding="utf-8"))
    d["sino_observed"] = SINO[sid]
    d["sino_declined"] = DECLINED[sid]
    json.dump(d, open(p,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

    S = {x["id"]: x for x in d["source"]["lines"]}
    T = {x["id"]: x for x in d["target"]["lines"]}
    uniq = set(d["unique_pairs"])
    res, acts, keeps, slotted = [], collections.Counter(), 0, 0
    mora_tot = 0
    for s in d["segments"]:
        if s["seg_id"] not in uniq:
            continue
        acts[s.get("obs","render?")] += 1
        if s.get("obs") == "keep":
            keeps += 1
        if s.get("slot_excluded") or s["type"].endswith(":0"):
            continue
        ko2ja = d["direction"] == "ko2ja"
        jp, kr = (s["tgt"], s["src"]) if ko2ja else (s["src"], s["tgt"])
        JP, KR = (T, S) if ko2ja else (S, T)
        m = sp = 0; skip = False
        for i in jp:
            ln = JP[i]
            if "reading_kana" in ln:
                a,b = morae(ln["reading_kana"]); m += a; sp += b
            elif latin_only(ln["text"]):
                skip = True
        if skip or m == 0:
            continue
        if any(has_latin(JP[i]["text"]) for i in jp) or any(has_latin(KR[i]["text"]) for i in kr):
            continue
        k = sum(syl(KR[i]["text"]) for i in kr)
        mora_tot += m
        res.append((m - sp - k) if ko2ja else (k - (m - sp)))
        slotted += 1
    n = len(uniq)
    ex  = 100*sum(1 for x in res if x == 0)/len(res) if res else 0
    w1  = 100*sum(1 for x in res if abs(x) <= 1)/len(res) if res else 0
    ko  = sum(syl(x["text"]) for x in d["target"]["lines"])
    print("%-6s %-24s %5d %5d %5.0f%% %5.0f%% %6d %6d  %s"
          % (sid, d["target"]["title"][:22], n, slotted, ex, w1,
             len(SINO[sid]), keeps,
             " ".join("%s=%d" % (k,v) for k,v in acts.most_common())))
    rows.append(dict(
      song_id=sid, cover_id=d["cover_id"], title_ko=d["target"]["title"],
      title_ja=d["source"]["title"], direction=d["direction"],
      original_artist=d["source"]["artist"], cover_channel=META[sid]["cover_channel"],
      cover_url=META[sid]["cover_url"], cover_kind=d["target"].get("kind",""),
      line_count=n, syllable_total_ko=ko, mora_total_ja=mora_tot,
      sino_ratio="%.3f" % (len(SINO[sid])/n) if n else "",
      loc_rate="%.3f" % ((n-keeps)/n) if n else "",
      lyrics_sha256_src=hashlib.sha256("\n".join(x["text"] for x in d["source"]["lines"]).encode()).hexdigest(),
      lyrics_sha256_tgt=hashlib.sha256("\n".join(x["text"] for x in d["target"]["lines"]).encode()).hexdigest(),
      slot_source="template", audio_sha256="",
      segment_count=len(d["segments"]),
      align_agreement="%.2f" % (ex/100) if res else "",
      is_gold=str(bool(d.get("is_gold"))).lower()))

cols = ["song_id","cover_id","title_ko","title_ja","direction","original_artist",
        "cover_channel","cover_url","cover_kind","line_count","syllable_total_ko",
        "mora_total_ja","sino_ratio","loc_rate","lyrics_sha256_src","lyrics_sha256_tgt",
        "slot_source","audio_sha256","segment_count","align_agreement","is_gold"]
with open("data/metadata.csv","w",encoding="utf-8",newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print("\ndata/metadata.csv — %d행" % len(rows))
allres = []
for sid in ["s001","s002","s003","s005"]:
    pass
