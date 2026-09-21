# -*- coding: utf-8 -*-
"""最終分析:覆寫校正 + 統計輸出 (stats.json / classified_all.csv)"""
import csv, glob, re, json
from collections import defaultdict, Counter

WS = r"C:/Users/ed249/Documents/kimi/tasks/2026-09-17/13-23-56-2cb8ea5d"
DAYS = [f"2026-09-{d:02d}" for d in range(9, 22)]

rows = []
for f in sorted(glob.glob(WS + "/news_csv/*.csv")):
    m = re.search(r"2026(\d{4})", f)
    snap = f"2026-{m.group(1)[:2]}-{m.group(1)[2:]}"
    with open(f, encoding="utf-8-sig") as fh:
        for row in list(csv.reader(fh))[1:]:
            if len(row) >= 4 and row[1].strip():
                title_full = row[1].strip()
                mm = re.search(r"\s-\s*([^-]+)$", title_full)
                src = mm.group(1).strip() if mm else ""
                base = re.sub(r"\s*-\s*[^-]*$", "", title_full).strip()
                base = re.sub(r"\s+", " ", base)
                rows.append({"snap": snap, "rank": int(row[0]), "title": base,
                             "src": src, "pub": row[3]})

CATS = {
    "AI科技": ["AI", "人工智慧", "iPhone", "蘋果發表會", "Apple", "摺疊", "無人載具",
             "機器人", "晶片", "半導體", "資安"],
    "經濟財經": ["台積電", "費半", "Fed", "升息", "美股", "道瓊", "標普", "台指期", "ADR",
              "原油", "油價", "布蘭特", "匯率", "股價", "記憶體股", "物價", "通膨",
              "人口連", "負成長", "炒房", "出生人口", "人口9年", "勞保", "健保費"],
    "娛樂影視": ["陳建州", "黑人", "范瑋琪", "范范", "小S", "星聞", "演唱會",
              "金鐘", "金馬", "布克獎", "楊双子", "金翎", "周玉琴", "賴岳謙"],
    "體育": ["棒球", "大聯盟", "NBA", "PLG", "友誼賽", "羽球", "網球", "足球", "奧運",
           "世足", "揮汗有禮"],
    "生活氣象": ["東北季風", "東北風", "颱風", "天氣", "氣象", "降雨", "溫度", "高溫", "地震",
              "風生活", "吳德榮", "淑麗", "杜鵑", "熱帶擾動", "聖嬰", "婚假", "國旅補助",
              "金目鯛", "赴東京"],
    "社會": ["護理師", "肇逃", "輾斃", "羈押", "聲押", "槍", "毒", "殺", "棄屍", "凶嫌",
           "起訴", "法辦", "詐", "賄", "選罷法", "午餐", "廚餘", "成淵", "迷姦", "下藥",
           "中彈", "警追緝", "看守所", "林祐嘉"],
    "國際": ["川普", "美軍", "伊朗", "胡塞", "葉門", "青年運動", "普亭", "普京",
           "烏克蘭", "俄羅斯", "煉油廠", "強生", "英相", "金磚", "莫迪", "習近平", "川習會",
           "習川會", "莫卡港", "曼德海峽", "紅海", "沙烏地", "沙國", "莫加", "油輪",
           "道瓊", "左派智庫", "沖繩", "印度"],
}
POL_WORDS = ["賴清德", "蕭美琴", "卓榮泰", "卓揆", "林佳龍", "沈伯洋", "蔡英文", "小英",
             "陳水扁", "蘇巧慧", "吳思瑤", "林岱樺", "柯建銘", "王義川", "洪申翰", "吳沛憶",
             "林延鳳", "洪健益", "民進黨", "綠營", "綠委", "新系", "賴政府", "賴桑",
             "蔣萬安", "蔣得立", "黃國昌", "柯文哲", "陳佩琪", "侯友宜", "李四川", "韓國瑜",
             "盧秀燕", "徐巧芯", "王鴻薇", "羅智強", "秦慧珠", "邱臣遠", "林杏兒", "陳見賢",
             "于北辰", "柯志恩", "高虹安", "何志勇", "徐欣瑩", "黃士修", "吳子嘉", "郭正亮",
             "國民黨", "藍營", "藍委", "民眾黨", "白營", "北市府", "蔣市府", "殷瑋",
             "高金素梅", "張俊傑", "谷立言", "AIT", "陸委會", "共諜", "中共", "統戰",
             "軍售", "金門海域", "台海", "不副署", "副署", "違憲", "監院", "監察院",
             "行政院", "立法院", "立委", "九合一", "選舉", "市長", "議員", "民調",
             "選情", "內閣", "國防", "國安", "中國台灣", "中國籍", "雙重國籍",
             "Chinese Taipei", "總統", "副總統", "大巨蛋", "青鳥", "藍白", "綠白", "棄保",
             "造勢", "顧問團", "政黨", "官邸", "朱安雄", "魏平政", "王惠美", "江啟臣"]

def classify(title):
    best, best_score = "其他", 0
    for cat, kws in CATS.items():
        s = sum(1 for k in kws if k in title)
        if s > best_score:
            best, best_score = cat, s
    if any(k in title for k in POL_WORDS):
        return "政治"
    return best if best_score > 0 else "其他"

GREEN = ["賴清德", "蕭美琴", "卓榮泰", "卓揆", "林佳龍", "沈伯洋", "蔡英文", "小英",
         "陳水扁", "蘇巧慧", "吳思瑤", "林岱樺", "柯建銘", "王義川", "洪申翰", "吳沛憶",
         "林延鳳", "洪健益", "民進黨", "綠營", "綠委", "新系", "賴政府", "賴桑",
         "行政院", "陸委會", "監院", "監察院", "鄭朝方", "總統府", "賴清德太太"]
BLUE = ["蔣萬安", "蔣得立", "黃國昌", "柯文哲", "陳佩琪", "侯友宜", "李四川", "韓國瑜",
        "盧秀燕", "徐巧芯", "王鴻薇", "羅智強", "秦慧珠", "邱臣遠", "林杏兒", "陳見賢",
        "于北辰", "柯志恩", "高虹安", "何志勇", "徐欣瑩", "黃士修", "吳子嘉", "郭正亮",
        "國民黨", "藍營", "藍委", "民眾黨", "白營", "北市府", "蔣市府", "殷瑋",
        "高金素梅", "張俊傑", "王偉忠", "黃暐瀚", "蔣萬安太太", "蔣萬安兒", "蔣得立"]

CRIT_VERBS = ["轟", "痛批", "批評", "開砲", "嗆", "酸", "諷", "打臉", "斥", "控",
              "質疑", "不滿", "火大", "出征", "抹黑", "爆料", "踢爆", "揭", "猛打",
              "開箱", "反擊", "還擊", "反嗆", "嗆聲", "砲轟", "哭吧", "氣炸", "怒"]
SCANDAL = ["羈押", "聲押", "起訴", "判刑", "共諜", "貪污", "弊案", "棄保", "潛逃",
           "逃亡", "挨告", "違憲", "違法", "惹議", "涉案", "被搜索", "侵吞"]
POS_WORDS = ["大讚", "肯定", "力挺", "支持", "讚", "聰明", "承諾", "突破", "破冰",
             "超麻吉", "讚賞", "相挺", "加持"]

def stance(title):
    g = [w for w in GREEN if w in title]
    b = [w for w in BLUE if w in title]
    has_crit = any(v in title for v in CRIT_VERBS) or any(v in title for v in SCANDAL)
    has_pos = any(v in title for v in POS_WORDS)
    target_camps, speaker_camps = set(), set()
    for v in CRIT_VERBS:
        idx = title.find(v)
        if idx >= 0:
            before = title[max(0, idx - 14):idx]
            after = title[idx + len(v): idx + len(v) + 30]
            for w in g:
                if w in after: target_camps.add("G")
                if w in before: speaker_camps.add("G")
            for w in b:
                if w in after: target_camps.add("B")
                if w in before: speaker_camps.add("B")
    if not target_camps and has_crit:
        if g: target_camps.add("G")
        if b: target_camps.add("B")
    if not g and not b:
        return "非政治"
    if has_crit:
        if target_camps == {"G"}: return "批執政"
        if target_camps == {"B"}: return "批在野"
        if target_camps == {"G", "B"}: return "互批"
        return "中性政治"
    if has_pos:
        camps = set()
        if g: camps.add("G")
        if b: camps.add("B")
        if camps == {"G"}: return "正面執政"
        if camps == {"B"}: return "正面在野"
        return "中性政治"
    return "中性政治"

# ---- 人工覆寫(逐條覆核後的修正) ----
OVERRIDE = {
 "中天6點聲明再控周玉琴！曝2段對話紀錄 斥責賴岳謙「謊稱被退通告」": ("娛樂影視", "非政治"),
 "李洋真加碼了！官網悄更新「揮汗有禮追加100萬份」 運動部：發完為止": ("體育", "非政治"),
 "沖繩變天 日布局「台灣有事」阻力大減": ("國際", "非政治"),
 "高雄前議長朱安雄中國病逝享壽82歲！曾叱吒南台灣政商界 骨灰今返台": ("政治", "中性政治"),
 "魏平政正妹女兒幫拍宣傳片 開場「1句話」被網友砲轟": ("政治", "批在野"),
 "新聞眼／川普批左派智庫 台灣掃到颱風尾": ("國際", "非政治"),
 "國安危機 台灣人口連32個月負成長": ("經濟財經", "非政治"),
 "今日（09/15）重點新聞！勞動部今發紅包，勞保年金「每人平均領19000」／14縣市長輩健保費「免申請政府自動代繳」／颱風杜鵑影響台灣嗎？": ("經濟財經", "非政治"),
 "IVE小巨蛋看板出現Chinese Taipei惹議 洪健益點名蔣萬安應立即回應": ("政治", "批在野"),
 "不副署被美國學者認證公然違憲郭正亮：賴清德已歷史留名- 政治": ("政治", "批執政"),
 "北市營養午餐爭議連爆！竟要學生「排隊秤廚餘」 林延鳳揭荒唐公文內幕": ("政治", "批在野"),
 "卓榮泰酸台北敬老卡只600點...市府回應使用範圍最廣 嗆卓助選搞政治": ("政治", "互批"),
 "反擊中國抗議歐洲議會副議長：接受蕭美琴邀請將訪問台灣| 政治": ("政治", "正面執政"),
 "林佳龍稱「台美共管中國」 學者：聞所未聞": ("政治", "批執政"),
 "幕僚諜影4-3》張俊傑擺老闆姿態 要求高金讓他掛公費助理": ("政治", "批在野"),
 "幕僚諜影4-4》高金案揭統戰台灣原住民藍圖 廈大16族田調藏玄機": ("政治", "批在野"),
 "年底大選「兩個人的武林」 他：蔣萬安選情不垮也人設半毀": ("政治", "批在野"),
 "成淵國中87人吃午餐狂拉！蔣萬安深夜發聲滅火 網抓包1亮點全歪樓": ("政治", "批在野"),
 "敲碗成功！沈伯洋正面迎擊「蔣萬安4年前考題」 王偉忠大讚：好聰明": ("政治", "正面執政"),
 "新竹藍白破局延燒！吳子嘉告白營9人 黃士修點名徐欣瑩「政治圈滅絕大君」": ("政治", "批在野"),
 "昔嗆不歡迎柯文哲來日本 日議員上畠寛弘與沈伯洋合體：研究吸菸區管理": ("政治", "正面執政"),
 "沈伯洋合體陳水扁！加LINE燦笑、抱娃傻眼照笑翻全網": ("政治", "正面執政"),
 "爆徐欣瑩民調數字「崩盤」 黃國昌嘆：國民黨利用完我們就一腳踹開": ("政治", "批在野"),
 "爆青鳥控蔣萬安太太「矮化國格」 藍議員火大轟：賤招一堆- 政治": ("政治", "互批"),
 "獨／藍白共挺高虹安、何志勇仍無黨參選 國民黨新竹市黨部決議撤銷黨籍": ("政治", "批在野"),
 "王偉忠指選情滿順、蔣萬安快昏了沈伯洋：提醒要關注市政問題| 政治": ("政治", "批在野"),
 "王偉忠讚沈伯洋選情順 指蔣萬安議會質詢「都快昏了」": ("政治", "批在野"),
 "監院查蔣得立「沒發公文直接打電話」 教育局長直言：與慣例不符": ("政治", "批在野"),
 "竹北藍白分裂 邱臣遠曝陳見賢私下提醒「你玩不過這些人」": ("政治", "批在野"),
 "蔣得立交換資格遭美取消？ 殷瑋指他仍在美國求學反問翁達瑞一事- 政治": ("政治", "批執政"),
 "蔣萬安妻昔喊Chinese Taipei遭出征 沈伯洋：應聚焦「是誰害我們用」": ("政治", "批在野"),
 "蕭美琴驚險突破封鎖抵義大利！北京不爽嗆卑鄙 他讚外交一事：見證歷史": ("政治", "正面執政"),
 "潛蕭美琴演講！他揭神秘女露餡：中國派人來": ("政治", "中性政治"),
 "綠營猛打蔣萬安兒矇到選票？名醫嗆：選舉亂打低估選民- 政治": ("政治", "互批"),
 "魚販送金目鯛祝「鴻運當頭」 沈伯洋超捧場接住網笑翻": ("政治", "正面執政"),
 "彭湖海線全面戒備 嚴防高金素梅「大帳房」張俊傑偷渡": ("政治", "中性政治"),
 # ---- 09/18–09/21 新增覆核 ----
 "「健康幣」10月上路 首年預估核發至少136億幣": ("生活氣象", "非政治"),
 "健康幣10月上路12月起兌換最多可累積1.3萬幣| 政治": ("生活氣象", "非政治"),
 "全公開！全台候選人犯罪「1黨洗榜」 驗證傅崐萁「沒2、3條不大尾」": ("政治", "非政治"),
 "前立委鄭汝芬100萬交保 謝家幹部接人、女兒謝衣鳯未現身": ("政治", "批在野"),
 "名古屋亞運／又遭打壓？亞奧會拒絕李洋入場「對方拿不出證明」 開村儀式台灣被迫退場": ("政治", "非政治"),
 "官冷民熱…兩岸趨緊張台獨最大變數| 兩岸關係大調查| 要聞": ("政治", "非政治"),
 "幕後／謝新隆狂言「輸了沒面子」釀禍 謝典霖議會宴客保溪湖本命區 她爆料掀風暴": ("政治", "批在野"),
 "快訊／台南連鎖機車行嚴重火災！鋼骨變形、新車燒毀…隔壁醫美診所遭殃": ("社會", "非政治"),
 "新北三重燒肉店火警多人2樓跳下逃生9送醫| 社會": ("社會", "非政治"),
 "燒肉SMILE三重店嚴重火警！9人跳樓逃生送醫 築間深夜發重訊": ("社會", "非政治"),
 "營建股明天要噴了？央行鬆綁信用管制馨傳智庫何世昌：猶如房市續命丸- 房市": ("經濟財經", "非政治"),
 "獨／高雄飛澳門班機遭鳥襲延誤 129名旅客從下午等到天黑還沒飛": ("社會", "非政治"),
 "王偉忠稱梁文傑「表情冷冷讓同胞寒冷」！妻林楚茵高EQ發聲了": ("政治", "批執政"),
 "童子賢：一黨獨大非台灣人福氣": ("政治", "批執政"),
 "被控「台灣間諜」遭中國關押 蔡金樹臉書發文：我回來了": ("政治", "非政治"),
 "謝典霖被抓Cheap：機關算盡太聰明連褲子都賠進去- 政治": ("社會", "非政治"),
 "酸蔣萬安英文青鳥糗寫錯字方恩格：酸民加油- 政治": ("政治", "批執政"),
 "魏平政聲援謝典霖喊「沒對價」！彰檢打臉：餐會又送蛋黃酥已超過千元": ("政治", "批在野"),
 "【更新】協助張俊傑脫逃第10人現形 吳東翰軍營拘提5萬交保": ("政治", "批在野"),
 "沈伯洋演說拋金句「自由民主沒有血緣」！1段話萬人瘋傳淚：有洋蔥": ("政治", "正面執政"),
 "沈伯洋談民主「一句話」全場安靜！ 媒體人感嘆：洋流不只聲量": ("政治", "正面執政"),
 "洋流到桃園...沈伯洋中壢合體黃世杰人潮爆滿掃夜市前先開簽名會| 縣市長議員選戰| 要聞": ("政治", "正面執政"),
 "洋流外溢桃園！沈伯洋合體黃世杰 中壢夜市擠爆了「現場人潮曝光」": ("政治", "正面執政"),
}

def norm(t):
    return re.sub(r"\s+", " ", t).strip()

SRC_MAP = {"udn.com": "UDN 聯合報", "UDN": "UDN 聯合報", "setn.com": "三立新聞",
           "Yahoo股市": "Yahoo新聞", "自由財經": "自由時報", "storm.mg": "風傳媒",
           "news.cnyes.com": "鉅亨網", "鏡週刊Mirror Media": "鏡週刊"}

for r in rows:
    r["title"] = norm(r["title"])
    r["src"] = SRC_MAP.get(r["src"], r["src"])
    key = r["title"]
    if key in OVERRIDE:
        r["cat"], r["stance"] = OVERRIDE[key]
    else:
        r["cat"] = classify(r["title"])
        r["stance"] = stance(r["title"])

# ---------- 統計 ----------
stories = {}
for r in rows:
    s = stories.setdefault(r["title"], {"cat": r["cat"], "stance": r["stance"],
                                        "n": 0, "days": set(), "sumrank": 0, "srcs": set()})
    s["n"] += 1
    s["days"].add(r["snap"])
    s["sumrank"] += r["rank"]
    s["srcs"].add(r["src"])

CATS_ORDER = ["政治", "國際", "經濟財經", "AI科技", "社會", "生活氣象", "娛樂影視", "體育", "其他"]

# 類別:比重(unique) + 聲量(appearances) + 逐日
cat_uni = Counter(s["cat"] for s in stories.values())
cat_app = Counter()
cat_day = {c: {d: 0 for d in DAYS} for c in CATS_ORDER}
for r in rows:
    cat_app[r["cat"]] += 1
    cat_day[r["cat"]][r["snap"]] += 1

# 焦點四大類逐日聲量
focus_day = {c: [cat_day[c][d] for d in DAYS] for c in ["政治", "AI科技", "經濟財經", "國際"]}

# 立場
STANCES = ["批執政", "批在野", "互批", "正面執政", "正面在野", "中性政治"]
pol_stories = {t: s for t, s in stories.items() if s["stance"] in STANCES}
st_uni = Counter(s["stance"] for s in pol_stories.values())
st_app = Counter()
st_day = {st: {d: 0 for d in DAYS} for st in STANCES}
for r in rows:
    if r["stance"] in STANCES:
        st_app[r["stance"]] += 1
        st_day[r["stance"]][r["snap"]] += 1

def ratio(gd, bd, md):
    tot = gd + bd + md
    return round(100 * (gd + 0.5 * md) / tot, 1) if tot else None

g_app = st_app["批執政"] + st_app["正面在野"] * 0  # 正面在野不計入批執政
stance_day = {d: {"G": st_day["批執政"][d], "B": st_day["批在野"][d],
                  "M": st_day["互批"][d]} for d in DAYS}
daily_ratio = {d: ratio(stance_day[d]["G"], stance_day[d]["B"], stance_day[d]["M"]) for d in DAYS}

# Top stories
top = sorted(stories.items(), key=lambda x: (-x[1]["n"], x[1]["sumrank"] / x[1]["n"]))[:12]

# 媒體來源
src_uni = Counter()
src_cat = defaultdict(Counter)
for t, s in stories.items():
    for src in s["srcs"]:
        if src:
            src_uni[src] += 1
            src_cat[src][s["cat"]] += 1

stats = {
    "days": DAYS,
    "n_files": len(glob.glob(WS + "/news_csv/*.csv")),
    "n_rows": len(rows),
    "n_unique": len(stories),
    "cat_uni": {c: cat_uni.get(c, 0) for c in CATS_ORDER},
    "cat_app": {c: cat_app.get(c, 0) for c in CATS_ORDER},
    "focus_day": focus_day,
    "st_uni": {s: st_uni.get(s, 0) for s in STANCES},
    "st_app": {s: st_app.get(s, 0) for s in STANCES},
    "st_day": {s: [st_day[s][d] for d in DAYS] for s in STANCES},
    "daily_ratio": [daily_ratio[d] for d in DAYS],
    "top_stories": [{"title": t, "cat": s["cat"], "stance": s["stance"], "n": s["n"],
                     "avg_rank": round(s["sumrank"] / s["n"], 1),
                     "days": sorted(s["days"])} for t, s in top],
    "src_uni": dict(src_uni.most_common(15)),
    "src_cat": {k: dict(v) for k, v in src_cat.items()},
    "pol_n_uni": len(pol_stories),
    "pol_n_app": sum(st_app.values()),
}

with open(WS + "/stats.json", "w", encoding="utf-8") as fh:
    json.dump(stats, fh, ensure_ascii=False, indent=1)

with open(WS + "/classified_all.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["快照日期", "排名", "標題", "類別", "立場", "來源", "發布時間"])
    for r in sorted(rows, key=lambda x: (x["snap"], x["rank"])):
        w.writerow([r["snap"], r["rank"], r["title"], r["cat"], r["stance"], r["src"], r["pub"]])

print(json.dumps({k: v for k, v in stats.items() if k not in ("top_stories", "src_cat")},
                 ensure_ascii=False, indent=1))
