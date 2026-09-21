# -*- coding: utf-8 -*-
"""GoogleNews_Top10_2026 CSV 彙整分析:類別分類 + 執政/在野立場判定"""
import csv, glob, re, json
from collections import defaultdict

WS = r"C:/Users/ed249/Documents/kimi/tasks/2026-09-17/13-23-56-2cb8ea5d"

# ---------- 1. 讀取 ----------
rows = []
for f in sorted(glob.glob(WS + "/news_csv/*.csv")):
    m = re.search(r"2026(\d{4})", f)
    snap = f"2026-{m.group(1)[:2]}-{m.group(1)[2:]}"
    with open(f, encoding="utf-8-sig") as fh:
        for row in list(csv.reader(fh))[1:]:
            if len(row) >= 4 and row[1].strip():
                title_full = row[1].strip()
                src = ""
                mm = re.search(r"\s-\s*([^-]+)$", title_full)
                if mm:
                    src = mm.group(1).strip()
                base = re.sub(r"\s*-\s*[^-]*$", "", title_full).strip()
                rows.append({"snap": snap, "rank": int(row[0]), "title": base,
                             "src": src, "pub": row[3], "file": f.split("/")[-1]})

# ---------- 2. 類別關鍵字 ----------
CATS = {
    "AI科技": ["AI", "人工智慧", "iPhone", "蘋果發表會", "Apple", "摺疊", "無人載具",
             "機器人", "晶片", "半導體", "資安", "智慧"],
    "經濟財經": ["台積電", "費半", "Fed", "升息", "降息", "美股", "道瓊", "標普", "台指期",
              "ADR", "原油", "油價", "布蘭特", "匯率", "台幣", "股價", "記憶體股", "經濟",
              "物價", "通膨", "人口連", "負成長", "炒房", "出生人口", "人口9年"],
    "娛樂影視": ["陳建州", "黑人", "范瑋琪", "范范", "小S", "星聞", "演唱會", "電影",
              "金鐘", "金馬", "布克獎", "楊双子", "金翎", "藝人"],
    "體育": ["棒球", "大聯盟", "NBA", "PLG／", "友誼賽", "羽球", "網球", "足球", "奧運", "世足"],
    "生活氣象": ["東北季風", "東北風", "颱風", "天氣", "氣象", "降雨", "溫度", "高溫", "地震",
              "風生活", "吳德榮", "淑麗", "杜鵑", "熱帶擾動", "聖嬰", "婚假", "國旅補助",
              "金目鯛", "航班"],
    "社會": ["護理師", "肇逃", "撞", "羈押", "聲押", "槍", "毒", "殺", "棄屍", "凶嫌",
           "起訴", "法辦", "詐", "賄", "選罷法", "午餐", "營養午餐", "廚餘", "成淵",
           "迷姦", "下藥", "中彈", "警追緝", "看守所", "炒魷魚"],
    "國際": ["川普", "美軍", "美國擊沉", "伊朗", "胡塞", "葉門", "青年運動", "普亭", "普京",
           "烏克蘭", "俄羅斯", "煉油廠", "強生", "英相", "金磚", "莫迪", "習近平", "川習會",
           "習川會", "莫卡港", "曼德海峽", "紅海", "沙烏地", "沙國", "莫加", "印度",
           "烏克蘭無視", "華府", "北京威脅", "油輪", "油輪", " Fed ", "道瓊"],
}
# 政治放最後(含兩岸、國防、選舉、憲政)
POL_WORDS = ["賴清德", "蕭美琴", "卓榮泰", "卓揆", "林佳龍", "沈伯洋", "蔡英文", "小英",
             "陳水扁", "蘇巧慧", "吳思瑤", "林岱樺", "柯建銘", "王義川", "洪申翰", "吳沛憶",
             "林延鳳", "洪健益", "民進黨", "綠營", "綠委", "新系", "賴政府", "賴桑",
             "蔣萬安", "蔣得立", "黃國昌", "柯文哲", "陳佩琪", "侯友宜", "李四川", "韓國瑜",
             "盧秀燕", "徐巧芯", "王鴻薇", "羅智強", "秦慧珠", "邱臣遠", "林杏兒", "陳見賢",
             "于北辰", "柯志恩", "高虹安", "何志勇", "徐欣瑩", "黃士修", "吳子嘉", "郭正亮",
             "國民黨", "藍營", "藍委", "民眾黨", "白營", "北市府", "蔣市府", "殷瑋",
             "高金素梅", "張俊傑", "谷立言", "AIT", "陸委會", "共諜", "中共", "中國入侵",
             "統戰", "軍售", "金門海域", "台海", "不副署", "副署", "違憲", "監院", "監察院",
             "憲法", "行政院", "立法院", "立委", "九合一", "選舉", "市長", "議員", "民調",
             "選情", "內閣", "國防", "國安", "外交", "中國台灣", "中國籍", "雙重國籍",
             "Chinese Taipei", "總統", "副總統", "大巨蛋", "青鳥", "藍白", "綠白", "棄保",
             "造勢", "顧問團", "政黨", "元首", "官邸", "第一夫人"]

def classify(title):
    best, best_score = "其他", 0
    for cat, kws in CATS.items():
        s = sum(1 for k in kws if k in title)
        if s > best_score:
            best, best_score = cat, s
    pol = sum(1 for k in POL_WORDS if k in title)
    # 政治涵蓋兩岸/國防/選舉;政治權重優先(只要提到政治人物/事件即歸政治)
    if pol > 0:
        return "政治"
    return best if best_score > 0 else "其他"

# ---------- 3. 陣營與立場 ----------
GREEN = ["賴清德", "蕭美琴", "卓榮泰", "卓揆", "林佳龍", "沈伯洋", "蔡英文", "小英",
         "陳水扁", "蘇巧慧", "吳思瑤", "林岱樺", "柯建銘", "王義川", "洪申翰", "吳沛憶",
         "林延鳳", "洪健益", "民進黨", "綠營", "綠委", "新系", "賴政府", "賴桑",
         "行政院", "陸委會", "監院", "監察院", "鄭朝方", "政府", "總統府"]
BLUE = ["蔣萬安", "蔣得立", "黃國昌", "柯文哲", "陳佩琪", "侯友宜", "李四川", "韓國瑜",
        "盧秀燕", "徐巧芯", "王鴻薇", "羅智強", "秦慧珠", "邱臣遠", "林杏兒", "陳見賢",
        "于北辰", "柯志恩", "高虹安", "何志勇", "徐欣瑩", "黃士修", "吳子嘉", "郭正亮",
        "國民黨", "藍營", "藍委", "民眾黨", "白營", "北市府", "蔣市府", "殷瑋",
        "高金素梅", "張俊傑", "王偉忠", "黃暐瀚"]
# 高金素梅/張俊傑:無黨籍但為國民黨團成員,歸在野陣營(分析方法論中註明)

CRIT_VERBS = ["轟", "痛批", "批評", "批:", "批:", "開砲", "嗆", "酸", "諷", "打臉",
              "斥", "控", "質疑", "不滿", "火大", "出征", "抹黑", "爆料", "踢爆", "揭",
              "揭發", "猛打", "開箱", "反擊", "還擊", "反嗆", "嗆聲", "砲轟", "嘲笑",
              "哭吧", "氣炸", "怒", "轟:", "嗆:"]
SCANDAL = ["羈押", "聲押", "起訴", "判刑", "共諜", "貪污", "弊案", "棄保", "潛逃",
           "逃亡", "挨告", "違憲", "違法", "爭議", "惹議", "遭查", "查辦", "涉案",
           "涉案", "被搜索", "法辦", "侵占", "侵吞"]
POS_WORDS = ["大讚", "肯定", "力挺", "支持", "讚", "聰明", "承諾", "突破", "破冰",
             "超麻吉", "讚賞", "喝采", "相挺", "加持"]
NEG_FOR_CAMP = ["質詢「都快昏了」", "快昏了"]

def mentioned(title, words):
    return [w for w in words if w in title]

def stance(title):
    """回傳 (label, detail): label ∈ 批執政/批在野/互批/正面執政/正面在野/中性政治/非政治"""
    g = mentioned(title, GREEN)
    b = mentioned(title, BLUE)
    has_crit = any(v in title for v in CRIT_VERBS) or any(v in title for v in SCANDAL)
    has_pos = any(v in title for v in POS_WORDS)

    # 目標判定:找批判動詞,看動詞後 25 字內(含「」)的對象
    target_camps = set()
    speaker_camps = set()
    for v in CRIT_VERBS:
        idx = title.find(v)
        if idx >= 0:
            before = title[max(0, idx - 14):idx]
            after = title[idx + len(v): idx + len(v) + 30]
            for w in g:
                if w in after:
                    target_camps.add("G")
                if w in before:
                    speaker_camps.add("G")
            for w in b:
                if w in after:
                    target_camps.add("B")
                if w in before:
                    speaker_camps.add("B")
    if not target_camps and has_crit:
        # 醜聞類或被動句:被批判對象=文中政治人物
        for w in g:
            target_camps.add("G")
        for w in b:
            target_camps.add("B")
        speaker_camps = set()

    if not g and not b:
        return ("非政治", "")
    if has_crit:
        if target_camps == {"G"}:
            return ("批執政", f"對象:{g}")
        if target_camps == {"B"}:
            return ("批在野", f"對象:{b}")
        if target_camps == {"G", "B"}:
            return ("互批", f"綠:{g} 藍:{b}")
        return ("中性政治", f"綠:{g} 藍:{b}")
    if has_pos:
        camps = set()
        if g: camps.add("G")
        if b: camps.add("B")
        if camps == {"G"}:
            return ("正面執政", f"對象:{g}")
        if camps == {"B"}:
            return ("正面在野", f"對象:{b}")
        return ("中性政治", f"綠:{g} 藍:{b}")
    return ("中性政治", f"綠:{g} 藍:{b}")

# ---------- 4. 執行分類 ----------
for r in rows:
    r["cat"] = classify(r["title"])
    r["stance"], r["stance_detail"] = stance(r["title"])

# ---------- 5. 輸出供人工覆核 ----------
seen = {}
for r in rows:
    seen.setdefault(r["title"], r)
with open(WS + "/review_labels.txt", "w", encoding="utf-8") as fh:
    for t, r in sorted(seen.items(), key=lambda x: (x[1]["cat"], x[0])):
        fh.write(f"{r['cat']} | {r['stance']} | {t} | {r['stance_detail']}\n")

print("rows:", len(rows), "unique:", len(seen))
from collections import Counter
print(Counter(r["cat"] for r in seen.values()))
print(Counter(r["stance"] for r in seen.values()))
