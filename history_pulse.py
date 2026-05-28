import sys, os, json, re, base64, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime
import random

TOKEN = os.environ.get("GH_TOKEN", "")
PUSH = os.environ.get("PUSH_TOKEN", "")
USER = "xhy0911"
REPO = "history-pulse"
URL = f"https://{USER}.github.io/{REPO}/"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_site")

SRC = [("OECD Edu","https://oecdedutoday.com/feed/","核心"),("Hechinger","https://hechingerreport.org/feed/","核心"),("Brookings Edu","https://www.brookings.edu/feed/?topic=education","核心"),("Harvard Ed","https://www.gse.harvard.edu/feed","核心"),("EduNext","https://www.educationnext.org/feed/","核心"),("EdWeek","https://www.edweek.org/feed/?topic=teaching","核心"),("Nature-History","https://www.nature.com/subjects/history.rss","CSSCI"),("Smithsonian","https://www.smithsonianmag.com/rss/history/","核心"),("JSTOR Daily","https://daily.jstor.org/feed/","核心")]

REGIONS = [
    {"name":"芬兰","type":"国家","tag":"北欧","desc":"芬兰教育被誉为全球标杆，中小学生上课时间短、作业少，但PISA成绩长期领先。1917年独立，曾是瑞典和俄罗斯的一部分。芬兰有18.8万个湖泊，被称为\"千湖之国\"。","history":"芬兰在12世纪被瑞典统治，1809年被俄罗斯吞并为大公国，1917年十月革命后宣布独立。1939年冬苏联入侵芬兰，芬兰顽强抵抗（冬季战争）。二战后保持中立，1995年加入欧盟，2023年加入北约。","edu":"芬兰教育体系以\"信任\"为核心——没有标准化考试、没有学校排名、没有督察。教师是硕士学历，社会地位极高。7岁才开始上小学，之前以游戏和社交为主。每节课后有15分钟户外活动。","detail":"人口：555万 | 面积：33.8万平方公里 | 首都：赫尔辛基 | 官方语言：芬兰语、瑞典语 | 货币：欧元 | 独立日：1917年12月6日"},
    {"name":"新加坡","type":"国家","tag":"东南亚","desc":"位于马来半岛南端，面积728平方公里，人口约564万。1965年独立，从一个渔村发展为全球金融中心。李光耀推行英语教育+母语双语政策，创造经济奇迹。","history":"1819年莱佛士建立英国贸易站，成为英国殖民地。1942年被日本占领。1963年加入马来西亚联邦，1965年被驱逐后独立。在李光耀领导下迅速现代化，成为亚洲四小龙之一。","edu":"新加坡教育以\"分流\"著称——小学四年级通过考试分流，中学再次分流。双语政策（英语+母语）是其核心特色。近年来推行\"少教多学\"改革，减少考试压力，强调全人教育。","detail":"人口：564万 | 面积：728平方公里 | 首都：新加坡市 | 官方语言：英语、华语、马来语、泰米尔语 | 货币：新加坡元 | 独立日：1965年8月9日"},
    {"name":"京都","type":"城市","tag":"东亚","desc":"日本古都，拥有17处UNESCO世界遗产。以金阁寺、伏见稻荷大社、岚山竹林闻名。保留了日本最完整的传统文化，茶道、花道、艺伎文化兴盛。","history":"794年桓武天皇迁都平安京（今京都），此后一千余年一直是日本首都。1868年明治维新后首都迁至东京。二战期间因美国历史学家劝阻，京都免于原子弹轰炸，古建筑得以完整保存。","edu":"京都有37所大学，其中京都大学是日本仅次于东京大学的第二学府，培养了14位诺贝尔奖得主。京都的教育强调传统文化与现代科学的融合。","detail":"人口：147万 | 面积：827平方公里 | 位置：日本本州岛中部 | 著名大学：京都大学 | UNESCO遗产：17处 | 著名景点：金阁寺、伏见稻荷大社、岚山"},
    {"name":"撒马尔罕","type":"城市","tag":"中亚","desc":"乌兹别克斯坦第二大城市，丝绸之路上的明珠。有2500年历史。雷吉斯坦广场被誉为\"中亚最壮观的建筑群\"。帖木儿帝国的首都。","history":"公元前7世纪建城。1370年帖木儿将撒马尔罕定为帝国首都，召集各地工匠建造壮丽的清真寺和陵墓。1868年被俄罗斯帝国占领。1991年乌兹别克斯坦独立后，撒马尔罕成为重要的旅游和文化中心。","edu":"撒马尔罕国立大学是中亚最古老的高等学府之一，其历史可追溯到帖木儿帝国时期的乌鲁伯格天文台和经学院。","detail":"人口：约100万 | 位置：乌兹别克斯坦东部 | 海拔：702米 | 著名建筑：雷吉斯坦广场、比比-哈内姆清真寺 | 世界遗产：撒马尔罕-文化交汇之地 (2001年)"},
    {"name":"墨西哥","type":"国家","tag":"拉丁美洲","desc":"北美洲第三大国家，面积196万平方公里。拥有69种土著语言。亡灵节（Día de Muertos）被列为UNESCO非物质文化遗产。龙舌兰酒（Tequila）原产地。","history":"公元前1200年奥尔梅克文明兴起。1325年阿兹特克帝国建立特诺奇蒂特兰城。1519年西班牙殖民者科尔特斯入侵，1521年阿兹特克灭亡。1810年米格尔·伊达尔戈发起独立战争，1821年独立。","edu":"墨西哥国立自治大学（UNAM）是拉丁美洲最大、最古老的大学，成立于1551年，拥有超过36万学生。2021年墨西哥通过教育改革，强调教育公平和教师专业发展。","detail":"人口：1.28亿 | 面积：196万平方公里 | 首都：墨西哥城 | 官方语言：西班牙语 | 货币：墨西哥比索 | 独立日：1810年9月16日"},
    {"name":"伊斯坦布尔","type":"城市","tag":"欧亚交界","desc":"世界上唯一横跨欧亚两洲的城市。原名君士坦丁堡。拥有1500万人口，是土耳其最大城市。圣索菲亚大教堂见证了一千多年的宗教变迁。","history":"公元330年罗马皇帝君士坦丁大帝定为东罗马帝国首都。1453年被奥斯曼帝国苏丹穆罕默德二世攻陷，改名伊斯坦布尔。1923年土耳其共和国成立后，首都迁至安卡拉。","edu":"伊斯坦布尔大学成立于1453年，是土耳其最古老的大学。近年来土耳其推行\"历史教育本土化\"改革，强调多元文化理解的教育理念。","detail":"人口：1500万 | 位置：博斯普鲁斯海峡两岸 | 著名建筑：圣索菲亚大教堂、蓝色清真寺 | 横跨：欧洲和亚洲 | 曾用名：拜占庭、君士坦丁堡 | 地铁：欧洲最古老之一"},
]

HISTORY_TERMS = [
    {"term":"年鉴学派","field":"历史学","def":"20世纪法国史学流派，主张\"总体史\"研究，关注长时段的结构性变化，而非传统政治史的事件叙述。代表人物布罗代尔提出\"地理时间、社会时间、事件时间\"三重时间观。","why":"理解这个学派，就理解了20世纪史学革命的核心。年鉴学派改变了历史学家看问题的方式——从\"谁做了什么事\"转向\"人们如何在特定环境中生活\""},
    {"term":"全球史","field":"历史学","def":"20世纪后期兴起的史学范式，超越民族国家的分析框架，关注跨区域联系、交流和比较。强调\"连接性\"而非\"特殊性\"，代表著作有麦克尼尔的《西方的兴起》。","why":"全球史帮助我们理解今日全球化的历史根源。比如：不是西方\"发现\"了世界，而是世界各地的联系网络一直存在。"},
    {"term":"记忆之场","field":"历史学","def":"法国史学家皮埃尔·诺拉提出的概念，指集体记忆凝聚的符号性场所或事物（如国庆日、纪念碑、档案）。认为现代社会的记忆已经断裂，需要人造的\"记忆之场\"来维系。","why":"为什么历史教育中要讲国庆日、纪念日？\"记忆之场\"理论告诉你——这些不是仪式，而是一个民族维持自我认同的方式。"},
    {"term":"核心素养","field":"教育学","def":"学生应具备的必备品格和关键能力，OECD于1997年提出。中国2016年发布《中国学生发展核心素养》，包括文化基础、自主发展、社会参与三大维度，共18个基本要点。","why":"这是理解全球教育改革的关键词。每个教师都应该问自己：我教的这门课，到底要培养学生什么核心素养？"},
    {"term":"最近发展区","field":"教育学","def":"维果茨基提出的学习理论，指学生独立解决问题的实际能力与在他人帮助下可达到的潜在能力之间的差距。教学应着眼于\"跳一跳够得着\"的区域。","why":"教学中最实用的理论之一。\"太难\"或\"太简单\"都不行，最好的教学就是把任务放在学生刚好需要一点帮助才能完成的程度。"},
    {"term":"元认知","field":"心理学","def":"对自己认知过程的认知和调控的能力。弗拉维尔于1970年代提出。包括元认知知识（知道什么策略有效）和元认知调控（计划、监控、评价）。","why":"这是区分优秀学习者和普通学习者的关键。优秀学生不只是更努力，而是更清楚地知道自己\"怎么学才有效\"。"},
]

BOOKS = [
    {"title":"《历史学是什么》","author":"葛剑雄","why":"了解历史学本质的最佳入门书。历史不仅有事实，更有解释和立场。适合准教师理解历史学科的本质。","summary":"葛剑雄教授用平实的语言回答\"历史是什么\"\"历史有什么用\"\"如何学历史\"三个基本问题。他提出：历史不是过去的简单记录，而是历史学家与史实之间的对话。同一个历史事件，不同时代、不同立场的人会有完全不同的叙述。"},
    {"title":"《全球通史》","author":"斯塔夫里阿诺斯","why":"全球史观的经典之作。从1500年前后的人类迁徙讲到当代全球化。","summary":"全书分为上下两册：上册讲人类从起源到公元1500年的演进（各文明独立发展），下册讲1500年以后的世界日益联系（欧洲崛起、殖民时代、世界大战、全球化）。核心观点：历史不是孤立发展的，各文明之间始终存在互动。"},
    {"title":"《万历十五年》","author":"黄仁宇","why":"以大历史观写明代一个平淡年份，却揭示了整个帝国体制的结构性困境。","summary":"1587年（万历十五年），表面上太平无事。但黄仁宇通过分析万历皇帝、张居正、申时行、戚继光、李贽等人的命运，揭示了明朝政治制度的深层矛盾——以道德代替法律的管理方式已经走到了尽头。叙事手法独特，既是学术也是文学。"},
    {"title":"《教学勇气》","author":"帕克·帕尔默","why":"好的教学不能降低到技术层面，来自教师的自我认同与完整。","summary":"帕尔默提出：教学不是技术活，而是教师内心世界的外在表达。他探讨了为什么很多教师怕教书、为什么教师之间缺乏真诚交流、如何保持教学的热情。\"好的教学是对学生的一种邀请，让他们进入一个可以学习的空间。\""},
    {"title":"《枪炮、病菌与钢铁》","author":"贾雷德·戴蒙德","why":"从地理和环境角度解释世界各大洲发展差异。","summary":"为什么欧洲人征服了美洲而非相反？戴蒙德的回答：不是因为种族或文化优势，而是地理环境使然——欧亚大陆的东西轴向有利于作物和牲畜的传播，而美洲的南北轴向阻碍了交流。此外，欧洲人有更多的驯化动物，带来了传染病的\"生物武器\"。"},
    {"title":"《思考，快与慢》","author":"丹尼尔·卡尼曼","why":"揭示人类思维的两种系统：快速直觉和缓慢理性。","summary":"卡尼曼通过几十年的实验研究，揭示了大脑的两个系统：系统1自动、快速、感性；系统2缓慢、理性、懒惰。我们以为自己是理性的，但实际上90%的决策由系统1做出。书中充满了令人惊讶的认知偏差实验，帮你识别自己的思维盲区。"},
]

HISTORY_EDU_KW = ["history","historical","teach","learn","educat","student","teacher","school","lesson","curricul","policy","reform","classroom","pedagogy","museum","heritage","archive"]

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
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0")
        resp = urllib.request.urlopen(req, timeout=5)
        raw = resp.read().decode("utf-8", errors="replace")
        results = re.findall(r'"([^"]+)"', raw)
        if results:
            translated = results[0]
            if translated.strip():
                _trans_cache[key] = translated
                return translated
    except:
        pass
    return text[:200]

def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

log("抓取RSS...")
art = []
seen = set()
for nm, url, lv in SRC:
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=12)
        txt = r.read().decode("utf-8", errors="replace")
        rt = ET.fromstring(txt)
        ns = ""
        if rt.tag == "{http://www.w3.org/2005/Atom}feed": ns = "{http://www.w3.org/2005/Atom}"
        its = rt.findall(".//item") or rt.findall(f".//{ns}entry")
        count = 0
        for it in its:
            t = (it.find("title") or it.find(f"{ns}title"))
            ti = t.text.strip() if t is not None and t.text else ""
            if not ti: continue
            de = it.find("description") or it.find(f"{ns}summary") or it.find("summary")
            ds = ""
            if de is not None:
                ds = de.text or "".join(de.itertext()) or ""
                ds = re.sub(r"<[^>]+>", "", ds).strip()[:300]
            if not any(k in (ti+ds).lower() for k in HISTORY_EDU_KW): continue
            if ti.lower() in seen: continue
            seen.add(ti.lower())
            lk = ""
            l = it.find("link") or it.find(f"{ns}link")
            if l is not None: lk = l.get("href","") or l.text or ""
            dt = ""
            for p in ["pubDate",f"{ns}published",f"{ns}updated"]:
                e = it.find(p)
                if e is not None and e.text:
                    dd = e.text.strip()[:10]
                    if re.match(r"\d{4}-\d{2}-\d{2}",dd): dt = dd; break
            sc = round(5.0 + {"CSSCI":2.5,"核心":1.5,"普通":0.5}.get(lv,0.5) + (1.0 if len(ti)>40 else 0), 1)
            cn_title = translate(ti)
            art.append({"id":len(art)+1,"title":ti,"title_cn":cn_title,"src":nm,"lv":lv,"sc":min(10,sc),"date":dt,"desc":ds,"link":lk})
            count += 1
            if count >= 8: break
    except:
        pass
    log(f"  {nm}")

art.sort(key=lambda a:-a["sc"])

day_num = datetime.now().timetuple().tm_yday
region = REGIONS[day_num % len(REGIONS)]
h_term1 = HISTORY_TERMS[(day_num * 2) % len(HISTORY_TERMS)]
h_term2 = HISTORY_TERMS[(day_num * 2 + 1) % len(HISTORY_TERMS)]
book = BOOKS[day_num % len(BOOKS)]

os.makedirs(DIR, exist_ok=True)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"Noto Sans SC",sans-serif;background:#f5f0eb;color:#2c1810;line-height:1.6}
a{color:#2d6a4f;text-decoration:none}
a:hover{text-decoration:underline}
nav{background:#2d6a4f;padding:12px 16px;color:#fff;text-align:center;font-size:15px;font-weight:700;position:sticky;top:0;z-index:100}
.c{max-width:800px;margin:0 auto;padding:16px}
h1{font-size:20px;color:#2d6a4f;margin:16px 0;text-align:center}
h2{font-size:16px;color:#2d6a4f;margin:20px 0 10px;border-bottom:2px solid #2d6a4f;padding-bottom:4px}
.card{background:#fff;border-radius:8px;padding:12px 14px;margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,.06);border-left:3px solid #2d6a4f;transition:.2s}
.card:hover{box-shadow:0 3px 10px rgba(0,0,0,.1)}
.card .m{font-size:11px;color:#888;margin-bottom:4px}
.card .en{font-size:13px;color:#666;font-style:italic;margin-bottom:2px}
.card .cn{font-size:14px;color:#2c1810;font-weight:600}
.reg{background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-radius:10px;padding:16px;margin-bottom:12px}
.reg .n{font-size:18px;font-weight:700;color:#1b5e20}
.reg .t{display:inline-block;background:#2d6a4f;color:#fff;padding:2px 10px;border-radius:10px;font-size:11px}
.reg .d{font-size:13px;color:#333;margin:6px 0;line-height:1.6}
.kb{background:#e3f2fd;border-radius:8px;padding:12px;margin-bottom:8px;border-left:3px solid #1565c0}
.kb .tm{font-size:15px;font-weight:700;color:#1565c0}
.kb .fd{font-size:11px;color:#888}
.kb .df{font-size:13px;color:#444;margin-top:4px;line-height:1.6}
.bb{background:#fff3e0;border-radius:8px;padding:12px;margin-bottom:8px;border-left:3px solid #e65100}
.bb .tl{font-size:15px;font-weight:700;color:#e65100}
.bb .au{font-size:12px;color:#888}
.bb .wy{font-size:13px;color:#444;margin-top:4px;line-height:1.6}
.f{text-align:center;padding:20px;color:#888;font-size:12px;border-top:1px solid #ddd;margin-top:30px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:8px}
.btn{display:inline-block;background:#2d6a4f;color:#fff;padding:6px 14px;border-radius:6px;font-size:12px;margin:4px 2px}
.d-reg{background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-radius:10px;padding:20px;margin-bottom:16px}
.d-reg h1{font-size:24px;color:#1b5e20;text-align:left}
.d-reg .tag{display:inline-block;background:#2d6a4f;color:#fff;padding:2px 12px;border-radius:10px;font-size:12px}
.d-reg .s{font-size:14px;color:#333;line-height:1.8;margin:10px 0}
.d-reg .info{background:#fff;border-radius:8px;padding:12px;margin-top:10px;font-size:13px;color:#555}
@media(max-width:600px){.g{grid-template-columns:1fr}}
"""

def pg(body):
    return f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>历史教育学·每日简报</title><style>{CSS}</style></head><body><nav>🎓 历史教育学 · 每日简报 · <a href='{URL}' style='color:#fff'>🌐</a></nav><div class='c'>{body}</div><div class='f'>每日更新 · 全球视野 · 充实你的知识储备</div></body></html>"

log("生成页面...")

# 地区详情页
reg_html = f"<div class='d-reg'><h1>🌍 {esc(region['name'])}</h1><div><span class='tag'>{esc(region['type'])}</span><span class='tag'>{esc(region['tag'])}</span></div><div class='s'><p><strong>快速了解：</strong>{esc(region['desc'])}</p><p><strong>📜 历史：</strong>{esc(region['history'])}</p><p><strong>🎓 教育：</strong>{esc(region['edu'])}</p></div><div class='info'>📋 {esc(region['detail'])}</div><p style='margin-top:12px'><a href='index.html' class='btn'>← 返回首页</a></p></div>"
open(os.path.join(DIR,"region.html"),"w",encoding="utf-8").write(pg(reg_html))

# 知识卡详情页
terms_html = ""
for t in [h_term1, h_term2]:
    terms_html += f"<div class='kb'><div class='tm'>📌 {esc(t['term'])}</div><div class='fd'>{esc(t['field'])}</div><div class='df'><strong>定义：</strong>{esc(t['def'])}</div><div class='df' style='margin-top:8px;color:#2d6a4f'><strong>为什么重要：</strong>{esc(t['why'])}</div></div>"
terms_html += f"<a href='index.html' class='btn'>← 返回首页</a>"
open(os.path.join(DIR,"knowledge.html"),"w",encoding="utf-8").write(pg(f"<h1>📌 今日知识卡</h1>{terms_html}"))

# 书籍详情页
book_html = f"<div class='bb'><div class='tl'>📖 {esc(book['title'])}</div><div class='au'>{esc(book['author'])}</div><div class='wy'><p><strong>推荐理由：</strong>{esc(book['why'])}</p><p style='margin-top:8px'><strong>📖 内容梗概：</strong>{esc(book['summary'])}</p></div></div><a href='index.html' class='btn'>← 返回首页</a>"
open(os.path.join(DIR,"book.html"),"w",encoding="utf-8").write(pg(book_html))

# 首页
articles_html = ""
for a in art[:8]:
    articles_html += f"<div class='card'><div class='m'>{esc(a['src'])} ⭐{a['sc']} {a['date'] if a['date'] else ''}</div><div class='en'>{esc(a['title'])}</div><div class='cn'>{esc(a.get('title_cn',''))}</div></div>"

body = ""
body += f"<div style='background:linear-gradient(135deg,#e8f5e9,#2d6a4f);color:#fff;padding:24px;border-radius:12px;text-align:center;margin-bottom:16px'><div style='font-size:18px;font-weight:700'>🎓 历史教育学</div><div style='font-size:12px;opacity:.9;margin-top:4px'>{datetime.now().strftime('%Y年%m月%d日')} · 你的每日知识早餐</div></div>"

body += f"<h2>📰 今日热点 <span style='font-size:12px;color:#888;font-weight:400'>({len(art)}篇)</span></h2>"
if art: body += articles_html
else: body += "<p style='color:#888;font-size:13px'>暂无热点，请稍后查看</p>"

body += f"<h2>🌍 认识一个地方 · <a href='region.html'>{esc(region['name'])}</a></h2>"
body += f"<div class='reg'><div class='n'>🌍 {esc(region['name'])}</div><div><span class='t'>{esc(region['type'])}</span><span class='t'>{esc(region['tag'])}</span></div><div class='d'>{esc(region['desc'][:200])}… <a href='region.html' style='font-size:12px'>[查看详情]</a></div></div>"

body += f"<h2>📌 今日知识卡 · <a href='knowledge.html'>查看全部</a></h2>"
for t in [h_term1, h_term2]:
    body += f"<div class='kb'><div class='tm'>📌 {esc(t['term'])}</div><div class='fd'>{esc(t['field'])}</div><div class='df'>{esc(t['def'][:100])}… <a href='knowledge.html' style='font-size:12px'>[详情]</a></div></div>"

body += f"<h2>📖 今日推荐 · <a href='book.html'>{esc(book['title'])}</a></h2>"
body += f"<div class='bb'><div class='tl'>📖 {esc(book['title'])}</div><div class='au'>{esc(book['author'])}</div><div class='wy'>{esc(book['why'][:120])}… <a href='book.html' style='font-size:12px'>[查看梗概]</a></div></div>"

open(os.path.join(DIR,"index.html"),"w",encoding="utf-8").write(pg(body))
log("页面生成完成")

HDRS = {"Authorization":"token "+TOKEN,"Accept":"application/vnd.github.v3+json"}
def sha(p):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/{USER}/{REPO}/contents/{p}",headers=HDRS),timeout=10).read()).get("sha")
    except: return None
def up(p,c):
    s = sha(p)
    b = {"message":"auto "+datetime.now().strftime("%Y-%m-%d"),"content":base64.b64encode(c).decode(),"branch":"main"}
    if s: b["sha"] = s
    r = urllib.request.Request(f"https://api.github.com/repos/{USER}/{REPO}/contents/{p}",data=json.dumps(b).encode(),headers=HDRS,method="PUT")
    r.add_header("Content-Type","application/json")
    try: urllib.request.urlopen(r,timeout=30); return True
    except: return False

fl = [f for f in os.listdir(DIR) if f.endswith(".html") or f=="articles.json"]
ok = 0
for f in fl:
    with open(os.path.join(DIR,f),"rb") as fh: c = fh.read()
    if up(f,c): ok += 1
log(f"上传 {ok}/{len(fl)}")

log("推送微信...")
today = datetime.now().strftime("%Y-%m-%d")
msg = f"<div style='background:linear-gradient(135deg,#e8f5e9,#2d6a4f);color:#fff;padding:16px;border-radius:10px;text-align:center'><strong style='font-size:17px'>🎓 历史教育学 · 每日简报</strong><br><span style='font-size:12px;opacity:.9'>{today}</span></div>"

if art:
    msg += "<h3 style='color:#2d6a4f;margin:10px 0 6px;font-size:14px'>📰 今日热点</h3>"
    for a in art[:3]:
        msg += f"<div style='margin:4px 0;padding:8px 10px;background:#f0f7f0;border-radius:6px'><div style='font-size:12px;color:#888;margin-bottom:2px'>⭐{a['sc']} · {esc(a['src'])}</div><div style='font-size:12px;color:#666;font-style:italic'>{esc(a['title'][:80])}</div><div style='font-size:13px;color:#2c1810;font-weight:600'>{esc(a.get('title_cn','')[:80])}</div></div>"

msg += f"<h3 style='color:#2d6a4f;margin:10px 0 6px;font-size:14px'>🌍 认识一个地方 · {esc(region['name'])}</h3>"
msg += f"<div style='padding:8px 10px;background:#e8f5e9;border-radius:6px;font-size:13px;color:#333;line-height:1.6'>{esc(region['desc'][:200])}</div>"

msg += "<h3 style='color:#2d6a4f;margin:10px 0 6px;font-size:14px'>📌 今日知识卡</h3>"
for t in [h_term1, h_term2]:
    msg += f"<div style='padding:6px 10px;background:#e3f2fd;border-radius:6px;margin:3px 0;border-left:3px solid #1565c0'><strong style='font-size:13px;color:#1565c0'>{esc(t['term'])}</strong> <span style='font-size:11px;color:#888'>· {esc(t['field'])}</span><p style='font-size:12px;color:#444;margin-top:2px'>{esc(t['def'][:100])}…</p></div>"

msg += f"<h3 style='color:#2d6a4f;margin:10px 0 6px;font-size:14px'>📖 今日推荐 · {esc(book['title'])}</h3>"
msg += f"<div style='padding:8px 10px;background:#fff3e0;border-radius:6px;border-left:3px solid #e65100'><strong style='font-size:13px;color:#e65100'>{esc(book['title'])}</strong> <span style='font-size:12px;color:#888'>- {esc(book['author'])}</span><p style='font-size:12px;color:#444;margin-top:4px'>{esc(book['why'][:120])}…</p></div>"

msg += f"<p style='text-align:center;margin:12px 0'><a href='{URL}' style='display:inline-block;background:#2d6a4f;color:#fff;padding:8px 20px;border-radius:6px;text-decoration:none;font-size:13px'>🌐 查看完整网站</a></p><p style='text-align:center;color:#aaa;font-size:11px'>每日更新 · 历史教育学 · 全球视野</p>"

b = json.dumps({"token":PUSH,"title":f"🎓历史教育学·每日简报 {today}","content":msg,"template":"html"}).encode()
r = urllib.request.Request("https://www.pushplus.plus/send",data=b,headers={"Content-Type":"application/json"})
try:
    rp = json.loads(urllib.request.urlopen(r,timeout=10).read())
    if rp.get("code")==200: log("✔推送成功")
    else: log(f"✖{rp}")
except Exception as e: log(f"✖{e}")
print(f"\n完成！{len(art)}篇")
