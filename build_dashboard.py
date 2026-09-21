# -*- coding: utf-8 -*-
"""由 stats.json 產生 self-contained dashboard.html(含完整報告區塊)"""
import json

WS = r"C:/Users/ed249/Documents/kimi/tasks/2026-09-17/13-23-56-2cb8ea5d"
stats = json.load(open(WS + "/stats.json", encoding="utf-8"))

# Markdown 報告 → HTML
from markdown_it import MarkdownIt
md_html = MarkdownIt("commonmark").enable("table").render(
    open(WS + "/統計報告.md", encoding="utf-8").read())

DATA = json.dumps(stats, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>台灣新聞輿情 Dashboard · Google News Top10 彙整分析 2026/09/09–09/21</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--bg:#e9f5f1;--card:#ffffff;--line:#cfe4dd;--fg:#0f3d39;--mut:#5d7f79;
--g:#0d9488;--b:#0284c7;--r:#e11d48;--y:#d97706;--p:#7c3aed;--o:#ea580c;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font-family:"Microsoft JhengHei","Noto Sans TC",sans-serif;padding:24px;max-width:1280px;margin:0 auto}
h1{font-size:22px;margin-bottom:4px;color:var(--fg)}
.sub{color:var(--mut);font-size:13px;margin-bottom:20px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;box-shadow:0 1px 3px rgba(15,61,57,.06)}
.kpi .v{font-size:26px;font-weight:700}
.kpi .l{color:var(--mut);font-size:12px;margin-top:2px}
.kpi .v.g{color:var(--g)}.kpi .v.b{color:var(--b)}.kpi .v.r{color:var(--r)}.kpi .v.y{color:var(--y)}.kpi .v.p{color:var(--p)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin-bottom:16px;box-shadow:0 1px 3px rgba(15,61,57,.06)}
.card h2{font-size:15px;margin-bottom:10px;color:var(--fg)}
.card .note{color:var(--mut);font-size:12px;margin-top:8px;line-height:1.6}
canvas{max-height:300px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:12px}
.badge{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;white-space:nowrap}
.b-pol{background:#f3eefe;color:var(--p)}.b-intl{background:#e6f3fb;color:var(--b)}
.b-eco{background:#fdf3e3;color:var(--y)}.b-ai{background:#fdeee3;color:var(--o)}
.b-soc{background:#fdebf0;color:var(--r)}.b-life{background:#e3f5f1;color:var(--g)}
.b-ent{background:#fdeaf4;color:#db2777}.b-spo{background:#e3f6f7;color:#0e7490}.b-oth{background:#eef2f1;color:var(--mut)}
.s-g{background:#fdebf0;color:var(--r)}.s-b{background:#e6f3fb;color:var(--b)}
.s-m{background:#fdf3e3;color:var(--y)}.s-ng{background:#e3f5f1;color:var(--g)}
.s-nb{background:#e6f3fb;color:var(--b)}.s-n{background:#eef2f1;color:var(--mut)}
.footer{color:var(--mut);font-size:12px;margin-top:8px;line-height:1.8}
.report{font-size:13px;line-height:1.9}
.report h1{font-size:20px;margin:10px 0 6px}
.report h2{font-size:16px;margin:18px 0 8px;border-bottom:1px solid var(--line);padding-bottom:6px}
.report p{margin:8px 0}
.report li{margin:4px 0}
.report table{width:100%;border-collapse:collapse;font-size:13px;margin:10px 0}
.report th,.report td{border:1px solid var(--line);padding:6px 10px}
.report th{background:#e3f5f1}
.report code{background:#e3f5f1;padding:1px 6px;border-radius:4px}
.report strong{color:var(--fg)}
</style>
</head>
<body>
<h1>台灣新聞輿情 Dashboard</h1>
<div class="sub">資料來源:G:\\我的雲端硬碟 GoogleNews_Top10_2026*.csv(38 個快照檔)· Google News 台灣熱門新聞 Top 10 · 期間 2026/09/09–09/21</div>

<div class="kpis" id="kpis"></div>

<div class="grid">
  <div class="card"><h2>新聞類別比重(獨立則數)</h2><canvas id="cPie"></canvas>
    <div class="note" id="nPie"></div></div>
  <div class="card"><h2>新聞類別聲量(上榜次數)</h2><canvas id="cBar"></canvas>
    <div class="note">同一則新聞在多日/多個快照重複上榜即累計,代表話題延續性。</div></div>
  <div class="card"><h2>政治 · AI · 經濟 · 國際 — 逐日聲量趨勢</h2><canvas id="cTrend"></canvas>
    <div class="note">政治聲量全期居冠(日均 15.8 次);國際隨美伊衝突與川習會前瞻起伏;AI/科技僅在蘋果發表會(09/10)前後進榜。</div></div>
  <div class="card"><h2>執政 vs 在野 — 批判聲量逐日堆疊</h2><canvas id="cStack"></canvas>
    <div class="note">僅計政治新聞中具批判/互批語態者。互批折半計入雙方。</div></div>
  <div class="card"><h2>政治新聞立場結構</h2><canvas id="cStance"></canvas>
    <div class="note" id="nStance"></div></div>
  <div class="card"><h2>每日「批判指向執政」比例走勢</h2><canvas id="cRatio"></canvas>
    <div class="note">公式:(批執政 + 互批×0.5) ÷ (批執政+批在野+互批)。越高代表當日輿情對執政黨越不利。</div></div>
</div>

<div class="card"><h2>聲量 Top 12 新聞</h2><div style="overflow-x:auto"><table id="tTop"></table></div></div>

<div class="grid">
  <div class="card"><h2>媒體來源聲量(不重複則數)</h2><canvas id="cSrc"></canvas></div>
  <div class="card"><h2>主要媒體 × 類別分布</h2><canvas id="cSrcCat"></canvas>
    <div class="note">各媒體進榜新聞的類別堆疊,可看出不同媒體的議題偏重。</div></div>
</div>

<div class="card"><h2>完整分析報告</h2><div class="report">__REPORT__</div></div>

<div class="footer" id="foot"></div>

<script>
const S = __DATA__;
const DAYS = S.days.map(d=>d.slice(5).replace('-','/'));
const CATS = ["政治","國際","經濟財經","AI科技","社會","生活氣象","娛樂影視","體育","其他"];
const CCOL = {政治:"#bc8cff",國際:"#58a6ff",經濟財經:"#d29922",AI科技:"#ff9e64",社會:"#f85149",生活氣象:"#3fb950",娛樂影視:"#f778ba",體育:"#39c5cf",其他:"#8b949e"};
Chart.defaults.color="#44625c";Chart.defaults.borderColor="#cfe4dd";Chart.defaults.font.family='"Microsoft JhengHei",sans-serif';

// KPI
const gA=S.st_app["批執政"],bA=S.st_app["批在野"],mA=S.st_app["互批"];
const critTot=gA+bA+mA;
const gShare=(100*(gA+0.5*mA)/critTot).toFixed(1), bShare=(100*(bA+0.5*mA)/critTot).toFixed(1);
const lastDay=S.days[S.days.length-1];
document.getElementById("kpis").innerHTML=[
 [S.days[0].slice(5).replace('-','/')+"–"+lastDay.slice(5).replace('-','/'),"分析期間("+S.days.length+"天)",""],
 [S.n_files,"快照檔案數","b"],[S.n_rows,"上榜總筆次","b"],[S.n_unique,"不重複新聞",""],
 [S.pol_n_uni,"政治類新聞","p"],
 [gShare+"%","批判聲量指向執政","r"],[bShare+"%","批判聲量指向在野","g"],
 [critTot,"批判/互批總筆次","y"]
].map(k=>`<div class="kpi"><div class="v ${k[2]}">${k[0]}</div><div class="l">${k[1]}</div></div>`).join("");
const critUni=S.st_uni["批執政"]+S.st_uni["批在野"]+S.st_uni["互批"];
document.getElementById("nPie").innerHTML=`以 ${S.n_unique} 則不重複新聞計算。政治(含選舉、兩岸、國防)佔大宗。`;
document.getElementById("nStance").innerHTML=`${S.pol_n_uni} 則政治相關新聞的語態分布。批判類(批執政+批在野+互批)${critUni} 則,佔 ${(100*critUni/S.pol_n_uni).toFixed(1)}%。`;

new Chart(cPie,{type:"doughnut",data:{labels:CATS,datasets:[{data:CATS.map(c=>S.cat_uni[c]),backgroundColor:CATS.map(c=>CCOL[c])}]},options:{plugins:{legend:{position:"right"}}}});
new Chart(cBar,{type:"bar",data:{labels:CATS,datasets:[{data:CATS.map(c=>S.cat_app[c]),backgroundColor:CATS.map(c=>CCOL[c])}]},options:{indexAxis:"y",plugins:{legend:{display:false}},scales:{x:{beginAtZero:true}}}});
new Chart(cTrend,{type:"line",data:{labels:DAYS,datasets:["政治","AI科技","經濟財經","國際"].map(c=>({label:c,data:S.focus_day[c],borderColor:CCOL[c],backgroundColor:CCOL[c],tension:.3,spanGaps:true}))},options:{scales:{y:{beginAtZero:true}}}});
new Chart(cStack,{type:"bar",data:{labels:DAYS,datasets:[
 {label:"批執政(綠營)",data:S.st_day["批執政"],backgroundColor:"#f85149"},
 {label:"批在野(藍白)",data:S.st_day["批在野"],backgroundColor:"#58a6ff"},
 {label:"互批",data:S.st_day["互批"],backgroundColor:"#d29922"}]},options:{scales:{x:{stacked:true},y:{stacked:true,beginAtZero:true}}}});
new Chart(cStance,{type:"doughnut",data:{labels:["批執政","批在野","互批","正面執政","正面在野","中性政治"],datasets:[{data:["批執政","批在野","互批","正面執政","正面在野","中性政治"].map(s=>S.st_uni[s]),backgroundColor:["#f85149","#58a6ff","#d29922","#3fb950","#1f6feb","#8b949e"]}]},options:{plugins:{legend:{position:"right"}}}});
new Chart(cRatio,{type:"line",data:{labels:DAYS,datasets:[{label:"批判指向執政 %",data:S.daily_ratio,borderColor:"#f85149",backgroundColor:"rgba(248,81,73,.12)",fill:true,tension:.3}]},options:{scales:{y:{min:0,max:100}}}});

// top stories table
const badge=c=>({政治:"b-pol",國際:"b-intl",經濟財經:"b-eco",AI科技:"b-ai",社會:"b-soc",生活氣象:"b-life",娛樂影視:"b-ent",體育:"b-spo",其他:"b-oth"}[c]||"b-oth");
const sbadge=s=>({"批執政":"s-g","批在野":"s-b","互批":"s-m","正面執政":"s-ng","正面在野":"s-nb"}[s]||"s-n");
document.getElementById("tTop").innerHTML="<tr><th>#</th><th>新聞標題</th><th>類別</th><th>立場</th><th>上榜</th><th>均名</th><th>出現日</th></tr>"+
 S.top_stories.map((t,i)=>`<tr><td>${i+1}</td><td>${t.title}</td><td><span class="badge ${badge(t.cat)}">${t.cat}</span></td><td><span class="badge ${sbadge(t.stance)}">${t.stance}</span></td><td>${t.n}</td><td>${t.avg_rank}</td><td style="white-space:nowrap">${t.days.map(d=>d.slice(5).replace('-','/')).join(", ")}</td></tr>`).join("");

// sources
const srcs=Object.keys(S.src_uni).slice(0,10);
new Chart(cSrc,{type:"bar",data:{labels:srcs,datasets:[{data:srcs.map(s=>S.src_uni[s]),backgroundColor:"#58a6ff"}]},options:{indexAxis:"y",plugins:{legend:{display:false}},scales:{x:{beginAtZero:true}}}});
new Chart(cSrcCat,{type:"bar",data:{labels:srcs,datasets:CATS.filter(c=>c!=="其他").map(c=>({label:c,data:srcs.map(s=>(S.src_cat[s]||{})[c]||0),backgroundColor:CCOL[c]}))},options:{scales:{x:{stacked:true},y:{stacked:true}}}});

document.getElementById("foot").innerHTML=
`方法說明:同一新聞標題跨快照去重後計為 1 則;「聲量」= 上榜筆次(重複進榜累計)。<br>
立場判定以關鍵字規則(批判動詞、醜聞詞、正面詞 + 政治人物陣營詞庫)自動分類,並經逐則人工覆核修正,惟標題語意複雜,仍可能存在少數誤判。<br>
「高金素梅/張俊傑」相關新聞歸入在野陣營(無黨籍,國民黨團成員)。資料期間 ${S.days[0].replace(/-/g,"/")}–${lastDay.replace(/-/g,"/")},共 ${S.n_files} 個快照、${S.n_rows} 筆上榜記錄、${S.n_unique} 則不重複新聞。`;
</script>
</body>
</html>"""

html = HTML.replace("__DATA__", DATA).replace("__REPORT__", md_html)
with open(WS + "/dashboard.html", "w", encoding="utf-8") as fh:
    fh.write(html)
print("dashboard.html written,", len(html), "bytes")
