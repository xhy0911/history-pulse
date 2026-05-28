import sys, os, json, re, base64, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime

TOKEN = os.environ.get("GH_TOKEN", "")
PUSH = os.environ.get("PUSH_TOKEN", "")
USER = "xhy0911"
REPO = "history-pulse"
URL = f"https://{USER}.github.io/{REPO}/"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_site")

SRC = [("OECD Edu","https://oecdedutoday.com/feed/","核心"),("Hechinger","https://hechingerreport.org/feed/","核心"),("Brookings Edu","https://www.brookings.edu/feed/?topic=education","核心"),("Harvard Ed","https://www.gse.harvard.edu/feed","核心"),("EduNext","https://www.educationnext.org/feed/","核心"),("EdWeek","https://www.edweek.org/feed/?topic=teaching","核心"),("Nature-History","https://www.nature.com/subjects/history.rss","CSSCI"),("Smithsonian","https://www.smithsonianmag.com/rss/history/","核心"),("JSTOR Daily","https://daily.jstor.org/feed/","核心")]

REGIONS = [
    {"name":"芬兰","type":"国家","tag":"北欧","desc":"芬兰教育被誉为全球标杆，中小学生上课时间短、作业少，但PISA成绩长期领先。1917年独立。","history":"12世纪被瑞典统治，1809年被俄罗斯吞并，1917年独立。","edu":"教师硕士学历，7岁才上小学，没有标准化考试。","detail":"人口：555万 | 首都：赫尔辛基 | 语言：芬兰语、瑞典语 | 独立日：1917年12月6日"},
    {"name":"新加坡","type":"国家","tag":"东南亚","desc":"面积728平方公里，1965年独立，从一个渔村发展为全球金融中心。","history":"1819年英国殖民地，1942年被日本占领，1965年独立。","edu":"双语政策（英语+母语），以分流制度著称。","detail":"人口：564万 | 首都：新加坡市 | 语言：英语、华语、马来语 | 独立日：1965年8月9日"},
    {"name":"京都","type":"城市","tag":"东亚","desc":"日本古都，拥有17处UNESCO世界遗产。保留最完整的传统文化。","history":"794年成为日本首都，1868年迁都东京，二战免于轰炸。","edu":"37所大学，京都大学培养14位诺贝尔奖得主。","detail":"人口：147万 | 大学：京都大学 | UNESCO遗产：17处"},
    {"name":"墨西哥","type":"国家","tag":"拉丁美洲","desc":"面积196万平方公里，69种土著语言。亡灵节闻名世界。","history":"1325年阿兹特克帝国建立，1521年被西班牙征服，1821年独立。","edu":"UNAM是拉美最大大学，36万学生。","detail":"人口：1.28亿 | 首都：墨西哥城 | 语言：西班牙语 | 独立日：1810年9月16日"},
    {"name":"伊斯坦布尔","type":"城市","tag":"欧亚交界","desc":"唯一横跨欧亚的城市，原名君士坦丁堡。1500万人口。","history":"330年罗马帝国定都，1453年被奥斯曼攻陷，1923年土耳其共和国成立。","edu":"伊斯坦布尔大学1453年成立，土耳其最古老大学。","detail":"人口：1500万 | 横跨欧亚 | 著名建筑：圣索菲亚大教堂"},
    {"name":"撒马尔罕","type":"城市","tag":"中亚","desc":"丝绸之路明珠，2500年历史。帖木儿帝国首都。","history":"前7世纪建城，1370年帖木儿定都，1868年被俄罗斯占领。","edu":"撒马尔罕国立大学是中亚最古老学府之一。","detail":"人口：100万 | 位置：乌兹别克斯坦 | 雷吉斯坦广场"},
]

TERMS = [
    {"term":"年鉴学派","field":"历史学","def":"20世纪法国史学流派，主张\"总体史\"研究，关注长时段的结构性变化，而非传统政治史的事件叙述。代表人物布罗代尔提出\"地理时间、社会时间、事件时间\"三重时间观。","why":"理解年鉴学派就理解了20世纪史学革命的核心——历史不是帝王将相的历史，而是普通人生活的历史。"},
    {"term":"全球史","field":"历史学","def":"超越民族国家的分析框架，关注跨区域联系、交流和比较。强调\"连接性\"而非\"特殊性\"。","why":"帮助理解今日全球化的历史根源——世界各地的联系网络一直存在，不是西方\"发现\"了世界。"},
    {"term":"记忆之场","field":"历史学","def":"法国史学家皮埃尔·诺拉提出的概念，指集体记忆凝聚的符号性场所或事物（如国庆日、纪念碑）。","why":"理解为什么历史教育中要讲国庆日、纪念日——这些是民族维持自我认同的方式。"},
    {"term":"核心素养","field":"教育学","def":"学生应具备的必备品格和关键能力。中国2016年发布三大维度：文化基础、自主发展、社会参与。","why":"全球教育改革的关键词。每个教师都应该问：我这门课到底要培养学生什么核心素养？"},
    {"term":"最近发展区","field":"教育学","def":"维果茨基提出，学生独立能力与在帮助下可达能力之间的差距。教学应着眼于\"跳一跳够得着\"的区域。","why":"教学中最好用的理论之一——太难或太简单都不行，最佳教学就是刚好需要一点帮助才能完成。"},
    {"term":"元认知","field":"心理学","def":"对自己认知过程的认知和调控能力。包括元认知知识（知道什么策略有效）和元认知调控（计划、监控、评价）。","why":"区分优秀学习者和普通学习者的关键——优秀学生不只是更努力，而是更清楚自己怎么学才有效。"},
]

BOOKS = [
    {"title":"《历史学是什么》","author":"葛剑雄","why":"了解历史学本质的最佳入门书。","summary":"葛剑雄教授用平实的语言回答\"历史是什么\"\"历史有什么用\"\"如何学历史\"三个基本问题。历史不是过去的简单记录，而是历史学家与史实之间的对话。"},
    {"title":"《全球通史》","author":"斯塔夫里阿诺斯","why":"全球史观的经典之作。","summary":"上下两册：上册讲人类从起源到1500年，下册讲1500年以后世界的日益联系。核心观点：历史不是孤立发展的，各文明之间始终存在互动。"},
    {"title":"《万历十五年》","author":"黄仁宇","why":"揭示明代帝国体制的结构性困境。","summary":"1587年表面上太平无事，但黄仁宇通过分析万历皇帝、张居正等人的命运，揭示了明朝以道德代替法律的管理方式已经走到尽头。"},
    {"title":"《教学勇气》","author":"帕克·帕尔默","why":"好的教学来自教师的自我认同。","summary":"教学不是技术活，而是教师内心世界的外在表达。好的教学是对学生的邀请，让他们进入一个可以学习的空间。"},
    {"title":"《枪炮、病菌与钢铁》","author":"贾雷德·戴蒙德","why":"从地理角度解释各大洲发展差异。","summary":"欧亚大陆的东西轴向有利于作物传播，美洲的南北轴向阻碍了交流。欧洲人不是更聪明，只是地理条件更好。"},
    {"title":"《思考，快与慢》","author":"丹尼尔·卡尼曼","why":"揭示人类思维的两种系统。","summary":"系统1自动快速感性，系统2缓慢理性懒惰。我们90%的决策由系统1做出。帮你识别自己的思维盲区。"},
]

HISTORY_EDU_KW = ["history","historical","teach","learn","educat","student","teacher","school","lesson","curricul","policy","reform","classroom","pedagogy","museum","heritage","archive","social studies","civics","college","university","academic"]

def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

_trans_cache = {}
def translate(text):
    if not text or len(text) < 5: return text or ""
    if re.search(r"[\u4e00-\u9fff]", text): return text
    key = text[:200]
    if key in _trans_cache: return _trans_cache[key]
    try:
        encoded = urllib.parse.quote(text[:2000])
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
        req = urllib.request.Request(url); req.add_header("User-Agent","Mozilla/5.0")
        resp = urllib.request.urlopen(req,timeout=5)
        raw = resp.read().decode("utf-8",errors="replace")
        results = re.findall(r'"([^"]+)"',raw)
        if results and results[0].strip():
            _trans_cache[key]=results[0]; return results[0]
    except: pass
    return text[:200]

def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

log("抓取RSS...")
art=[]; seen=set()
for nm,url,lv in SRC:
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=12)
        txt=r.read().decode("utf-8",errors="replace")
        rt=ET.fromstring(txt); ns=""
        if rt.tag=="{http://www.w3.org/2005/Atom}feed": ns="{http://www.w3.org/2005/Atom}"
        its=rt.findall(".//item") or rt.findall(f".//{ns}entry"); c=0
        for it in its:
            t=(it.find("title") or it.find(f"{ns}title"))
            ti=t.text.strip() if t is not None and t.text else ""
            if not ti: continue
            de=it.find("description") or it.find(f"{ns}summary") or it.find("summary")
            ds=""
            if de is not None: ds=(de.text or "".join(de.itertext()) or ""); ds=re.sub(r"<[^>]+>","",ds).strip()[:300]
            if not any(k in (ti+ds).lower() for k in HISTORY_EDU_KW): continue
            if ti.lower() in seen: continue
            seen.add(ti.lower())
            lk=""; l=it.find("link") or it.find(f"{ns}link")
            if l is not None: lk=l.get("href","") or l.text or ""
            dt=""
            for p in ["pubDate",f"{ns}published",f"{ns}updated"]:
                e=it.find(p)
                if e is not None and e.text:
                    dd=e.text.strip()[:10]
                    if re.match(r"\d{4}-\d{2}-\d{2}",dd): dt=dd; break
            sc=round(5.0+{"CSSCI":2.5,"核心":1.5,"普通":0.5}.get(lv,0.5)+(1.0 if len(ti)>40 else 0),1)
            cn=translate(ti)
            art.append({"id":len(art)+1,"title":ti,"cn":cn,"src":nm,"lv":lv,"sc":min(10,sc),"date":dt,"desc":ds,"link":lk}); c+=1
            if c>=8: break
    except: pass
    log(f"  {nm}")

art.sort(key=lambda a:-a["sc"])
day_num=datetime.now().timetuple().tm_yday
rg=REGIONS[day_num%len(REGIONS)]
tm1=TERMS[(day_num*2)%len(TERMS)]
tm2=TERMS[(day_num*2+1)%len(TERMS)]
bk=BOOKS[day_num%len(BOOKS)]
os.makedirs(DIR,exist_ok=True)

STYLE="""
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"Noto Sans SC",sans-serif;background:#f5f0eb;color:#2c1810;line-height:1.6}
a{color:#2d6a4f;text-decoration:none}
a:hover{text-decoration:underline}
nav{background:#2d6a4f;padding:12px 16px;color:#fff;text-align:center;font-size:14px;font-weight:700;position:sticky;top:0;z-index:100}
nav a{color:#fff;margin:0 6px}
.c{max-width:800px;margin:0 auto;padding:16px}
h1{font-size:20px;color:#2d6a4f;margin:16px 0;text-align:center}
h2{font-size:16px;color:#2d6a4f;margin:20px 0 10px;border-bottom:2px solid #2d6a4f;padding-bottom:4px}
.card{background:#fff;border-radius:8px;padding:12px 14px;margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,.06);border-left:3px solid #2d6a4f}
.card .m{font-size:11px;color:#888;margin-bottom:4px}
.card .en{font-size:13px;color:#666;font-style:italic;margin-bottom:2px}
.card .cn{font-size:14px;color:#2c1810;font-weight:600}
.reg{background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-radius:10px;padding:16px;margin-bottom:12px}
.reg .n{font-size:18px;font-weight:700;color:#1b5e20}
.reg .t{display:inline-block;background:#2d6a4f;color:#fff;padding:2px 10px;border-radius:10px;font-size:11px;margin:4px 2px}
.reg .d{font-size:13px;color:#333;margin:6px 0;line-height:1.6}
.kb{background:#e3f2fd;border-radius:8px;padding:12px;margin-bottom:8px;border-left:3px solid #1565c0}
.kb .tm{font-size:15px;font-weight:700;color:#1565c0}
.kb .fd{font-size:11px;color:#888}
.kb .df{font-size:13px;color:#444;margin-top:4px;line-height:1.6}
.bb{background:#fff3e0;border-radius:8px;padding:12px;margin-bottom:8px;border-left:3px solid #e65100}
.bb .tl{font-size:15px;font-weight:700;color:#e65100}
.bb .au{font-size:12px;color:#888}
.bb .wy{font-size:13px;color:#444;margin-top:4px;line-height:1.6}
.btn{display:inline-block;background:#2d6a4f;color:#fff!important;padding:8px 16px;border-radius:6px;font-size:13px;margin:6px 4px 0 0}
.btn:hover{opacity:.85}
.f{text-align:center;padding:20px;color:#888;font-size:12px;border-top:1px solid #ddd;margin-top:30px}
.l{max-width:700px;margin:0 auto}
.l h1{font-size:22px;text-align:left;margin-bottom:12px}
.l .lt{font-size:12px;color:#888;margin-bottom:8px}
.l .bd{background:#faf8f5;padding:16px;border-radius:8px;border-left:3px solid #2d6a4f;font-size:14px;line-height:1.8;color:#444;margin-bottom:16px}
@media(max-width:600px){.g{grid-template-columns:1fr}}
"""

def hd(): return f"<nav>🎓 历史教育学 · <a href='index.html'>首页</a><a href='{URL}'>🌐</a></nav>"
def ft(): return f"<div class='f'>每日更新 · 历史教育学 · 全球视野</div>"

def pg(body): return f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>历史教育学</title><style>{STYLE}</style></head><body>{hd()}<div class='c'>{body}</div>{ft()}</body></html>"

def pg2(title,body): return f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>{esc(title)}</title><style>{STYLE}</style></head><body>{hd()}<div class='c l'>{body}</div>{ft()}</body></html>"

log("生成页面...")

# 首页
art_html=""
for a in art:
    art_html+=f"<a href='article_{a['id']}.html' style='display:block;color:inherit;text-decoration:none'><div class='card'><div class='m'>{esc(a['src'])} ⭐{a['sc']} {a['date'] if a['date'] else ''}</div><div class='en'>{esc(a['title'])}</div><div class='cn'>{esc(a.get('cn',''))}</div></div></a>"

reg_html=f"<div class='reg'><div class='n'>🌍 {esc(rg['name'])}</div><div><span class='t'>{esc(rg['type'])}</span><span class='t'>{esc(rg['tag'])}</span></div><div class='d'>{esc(rg['desc'])}<br>{esc(rg['history'])}<br>{esc(rg['edu'])}</div><a href='region.html' class='btn'>查看详情</a></div>"

k_html=""
for t in [tm1,tm2]:
    k_html+=f"<div class='kb'><div class='tm'>📌 {esc(t['term'])}</div><div class='fd'>{esc(t['field'])}</div><div class='df'>{esc(t['def'][:120])}… <a href='knowledge.html'>[详情]</a></div></div>"

bk_html=f"<div class='bb'><div class='tl'>📖 {esc(bk['title'])}</div><div class='au'>{esc(bk['author'])}</div><div class='wy'>{esc(bk['why'])}<br><a href='book.html' style='font-size:12px'>[查看梗概]</a></div></div>"

body=f"<div style='background:linear-gradient(135deg,#e8f5e9,#2d6a4f);color:#fff;padding:24px;border-radius:12px;text-align:center;margin-bottom:16px'><div style='font-size:20px;font-weight:700'>🎓 历史教育学</div><div style='font-size:13px;opacity:.9;margin-top:4px'>{datetime.now().strftime('%Y年%m月%d日')} · 你的每日知识早餐</div></div>"
body+=f"<h2>📰 今日热点</h2>{art_html if art else '<p style=color:#888;font-size:13px>暂无</p>'}"
body+=f"<h2>🌍 认识一个地方</h2>{reg_html}"
body+=f"<h2>📌 今日知识卡 · <a href='knowledge.html' style='font-size:12px'>全部</a></h2>{k_html}"
body+=f"<h2>📖 今日推荐 · <a href='book.html' style='font-size:12px'>梗概</a></h2>{bk_html}"
open(os.path.join(DIR,"index.html"),"w",encoding="utf-8").write(pg(body))

# 地区详情
d=f"<h1>🌍 {esc(rg['name'])}</h1><div class='lt'><span class='t'>{esc(rg['type'])}</span> <span class='t'>{esc(rg['tag'])}</span></div>"
d+=f"<div class='bd'><p><strong>概况：</strong>{esc(rg['desc'])}</p><p style='margin-top:8px'><strong>📜 历史：</strong>{esc(rg['history'])}</p><p style='margin-top:8px'><strong>🎓 教育：</strong>{esc(rg['edu'])}</p><p style='margin-top:8px;font-size:13px;color:#555'><strong>📋 基本信息：</strong>{esc(rg['detail'])}</p></div>"
d+=f"<a href='index.html' class='btn'>← 返回首页</a>"
open(os.path.join(DIR,"region.html"),"w",encoding="utf-8").write(pg2(esc(rg['name']),d))

# 知识卡
k=f"<h1>📌 今日知识卡</h1>"
for t in [tm1,tm2]:
    k+=f"<div class='kb' style='margin-top:12px'><div class='tm'>📌 {esc(t['term'])}</div><div class='fd'>{esc(t['field'])}</div><div class='df'><strong>定义：</strong>{esc(t['def'])}</div><div class='df' style='margin-top:8px;color:#2d6a4f'><strong>💡 为什么重要：</strong>{esc(t['why'])}</div></div>"
k+=f"<a href='index.html' class='btn'>← 返回首页</a>"
open(os.path.join(DIR,"knowledge.html"),"w",encoding="utf-8").write(pg2("今日知识卡",k))

# 书籍
b=f"<h1>📖 {esc(bk['title'])}</h1><div class='lt'>{esc(bk['author'])}</div>"
b+=f"<div class='bd'><p><strong>推荐理由：</strong>{esc(bk['why'])}</p><p style='margin-top:12px'><strong>📖 内容梗概：</strong></p><p>{esc(bk['summary'])}</p></div>"
b+=f"<a href='index.html' class='btn'>← 返回首页</a>"
open(os.path.join(DIR,"book.html"),"w",encoding="utf-8").write(pg2(bk['title'],b))

# 文章详情页
for a in art:
    lc={"CSSCI":"c1","核心":"c2","普通":"c3"}.get(a["lv"],"c3")
    bd=f"<h1>{esc(a['title'])}</h1><div class='lt'>{esc(a['src'])} · ⭐{a['sc']} · {a['lv']} · {a['date'] if a['date'] else ''}</div>"
    bd+=f"<div class='bd'><p style='margin-bottom:12px'><strong>中文：</strong></p><p>{esc(a.get('cn',''))}</p><hr style='border:none;border-top:1px solid #ddd;margin:16px 0'><p><strong>原文：</strong></p><p style='font-family:Georgia,serif;font-size:13px;color:#666;margin-top:6px'>{esc(a['title'])}</p></div>"
    bd+=f"<div>"
    if a["link"]: bd+=f"<a href='{esc(a['link'])}' target='_blank' class='btn'>🔗 查看原文</a>"
    bd+=f"<a href='index.html' class='btn'>← 返回首页</a></div>"
    open(os.path.join(DIR,f"article_{a['id']}.html"),"w",encoding="utf-8").write(pg2(a["title"],bd))

log(f"页面: 首页 + 地区 + 知识 + 书籍 + {len(art)}篇文章")

# 部署
HDRS={"Authorization":"token "+TOKEN,"Accept":"application/vnd.github.v3+json"}
def sha(p):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/{USER}/{REPO}/contents/{p}",headers=HDRS),timeout=10).read()).get("sha")
    except: return None
def up(p,c):
    s=sha(p); b={"message":"auto "+datetime.now().strftime("%Y-%m-%d"),"content":base64.b64encode(c).decode(),"branch":"main"}
    if s: b["sha"]=s
    r=urllib.request.Request(f"https://api.github.com/repos/{USER}/{REPO}/contents/{p}",data=json.dumps(b).encode(),headers=HDRS,method="PUT")
    r.add_header("Content-Type","application/json")
    try: urllib.request.urlopen(r,timeout=30); return True
    except: return False

fl=[f for f in os.listdir(DIR) if f.endswith(".html") or f=="articles.json"]; ok=0
for f in fl:
    with open(os.path.join(DIR,f),"rb") as fh: c=fh.read()
    if up(f,c): ok+=1
log(f"上传 {ok}/{len(fl)}")

# 推送
log("推送微信...")
today=datetime.now().strftime("%Y-%m-%d")
msg=f"<div style='background:linear-gradient(135deg,#e8f5e9,#2d6a4f);color:#fff;padding:16px;border-radius:10px;text-align:center'><strong style='font-size:17px'>🎓 历史教育学 · 每日简报</strong><br><span style='font-size:12px;opacity:.9'>{today}</span></div>"
if art:
    msg+="<h3 style='color:#2d6a4f;margin:10px 0 6px;font-size:14px'>📰 今日热点</h3>"
    for a in art[:3]:
        msg+=f"<div style='margin:4px 0;padding:8px 10px;background:#f0f7f0;border-radius:6px'><div style='font-size:12px;color:#888'>{esc(a['src'])} ⭐{a['sc']}</div><div style='font-size:12px;color:#666;font-style:italic'>{esc(a['title'][:80])}</div><div style='font-size:13px;color:#444;font-weight:600'>{esc(a.get('cn','')[:80])}</div></div>"
msg+=f"<h3 style='color:#2d6a4f;margin:10px 0 6px;font-size:14px'>🌍 认识 · {esc(rg['name'])}</h3><div style='padding:8px 10px;background:#e8f5e9;border-radius:6px;font-size:13px;color:#333'>{esc(rg['desc'])}<br>{esc(rg['history'])}<br>{esc(rg['edu'])}</div>"
msg+="<h3 style='color:#2d6a4f;margin:10px 0 6px;font-size:14px'>📌 今日知识卡</h3>"
for t in [tm1,tm2]:
    msg+=f"<div style='padding:6px 10px;background:#e3f2fd;border-radius:6px;margin:3px 0;border-left:3px solid #1565c0'><strong style='font-size:13px;color:#1565c0'>{esc(t['term'])}</strong> <span style='font-size:11px;color:#888'>· {esc(t['field'])}</span><p style='font-size:12px;color:#444;margin-top:2px'>{esc(t['def'][:100])}…</p></div>"
msg+=f"<h3 style='color:#2d6a4f;margin:10px 0 6px;font-size:14px'>📖 {esc(bk['title'])}</h3><div style='padding:8px 10px;background:#fff3e0;border-radius:6px;border-left:3px solid #e65100;font-size:12px;color:#444'><strong>{esc(bk['title'])}</strong> - {esc(bk['author'])}<p style='margin-top:4px'>{esc(bk['summary'][:120])}…</p></div>"
msg+=f"<p style='text-align:center;margin:12px 0'><a href='{URL}' style='display:inline-block;background:#2d6a4f;color:#fff;padding:8px 20px;border-radius:6px;text-decoration:none;font-size:13px'>🌐 点此查看详情</a></p>"
b=json.dumps({"token":PUSH,"title":f"🎓历史教育学 {today}","content":msg,"template":"html"}).encode()
r=urllib.request.Request("https://www.pushplus.plus/send",data=b,headers={"Content-Type":"application/json"})
try:
    rp=json.loads(urllib.request.urlopen(r,timeout=10).read())
    if rp.get("code")==200: log("✔推送成功")
    else: log(f"✖{rp}")
except Exception as e: log(f"✖{e}")
print(f"\n完成！{len(art)}篇")
