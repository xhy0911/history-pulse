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

# 地区知识库（每天轮流推送一个）
REGIONS = [
    {"name":"芬兰","type":"国家","tag":"北欧","desc":"芬兰教育被誉为全球标杆，中小学生上课时间短、作业少，但PISA成绩长期领先。1917年独立，曾是瑞典和俄罗斯的一部分。芬兰有18.8万个湖泊，被称为\"千湖之国\"。","history":"芬兰在12世纪被瑞典统治，1809年被俄罗斯吞并为大公国，1917年十月革命后宣布独立。1939年冬苏联入侵芬兰，芬兰顽强抵抗（冬季战争）。二战后保持中立，1995年加入欧盟，2023年加入北约。"},
    {"name":"新加坡","type":"国家","tag":"东南亚","desc":"位于马来半岛南端，面积728平方公里，人口约564万。1965年独立，从一个渔村发展为全球金融中心。李光耀推行英语教育+母语双语政策，创造经济奇迹。","history":"1819年莱佛士建立英国贸易站，成为英国殖民地。1942年被日本占领。1963年加入马来西亚联邦，1965年被驱逐后独立。在李光耀领导下迅速现代化，成为亚洲四小龙之一。"},
    {"name":"墨西哥","type":"国家","tag":"拉丁美洲","desc":"北美洲第三大国家，面积196万平方公里。拥有69种土著语言。亡灵节（Día de Muertos）被列为UNESCO非物质文化遗产。龙舌兰酒（Tequila）原产地。","history":"公元前1200年奥尔梅克文明兴起。1325年阿兹特克帝国建立特诺奇蒂特兰城。1519年西班牙殖民者科尔特斯入侵，1521年阿兹特克灭亡。1810年米格尔·伊达尔戈发起独立战争，1821年独立。"},
    {"name":"撒马尔罕","type":"城市","tag":"中亚","desc":"乌兹别克斯坦第二大城市，丝绸之路上的明珠。有2500年历史。雷吉斯坦广场被誉为\"中亚最壮观的建筑群\"。帖木儿帝国的首都。","history":"公元前7世纪建城。1370年帖木儿将撒马尔罕定为帝国首都，召集各地工匠建造壮丽的清真寺和陵墓。1868年被俄罗斯帝国占领。1991年乌兹别克斯坦独立后，撒马尔罕成为重要的旅游和文化中心。"},
    {"name":"京都","type":"城市","tag":"东亚","desc":"日本古都，拥有17处UNESCO世界遗产。以金阁寺、伏见稻荷大社、岚山竹林闻名。保留了日本最完整的传统文化，茶道、花道、艺伎文化兴盛。","history":"794年桓武天皇迁都平安京（今京都），此后一千余年一直是日本首都。1868年明治维新后首都迁至东京。二战期间因美国历史学家劝阻，京都免于原子弹轰炸，古建筑得以完整保存。"},
    {"name":"伊斯坦布尔","type":"城市","tag":"欧亚交界","desc":"世界上唯一横跨欧亚两洲的城市。原名君士坦丁堡。拥有1500万人口，是土耳其最大城市。圣索菲亚大教堂见证了一千多年的宗教变迁。","history":"公元330年罗马皇帝君士坦丁大帝定为东罗马帝国首都。1453年被奥斯曼帝国苏丹穆罕默德二世攻陷，改名伊斯坦布尔。1923年土耳其共和国成立后，首都迁至安卡拉，但伊斯坦布尔仍是经济文化中心。"},
    {"name":"埃及","type":"国家","tag":"北非","desc":"文明古国，金字塔是唯一幸存的古代世界七大奇迹。尼罗河每年泛滥带来的肥沃土壤孕育了古埃及文明。人口约1.1亿，首都开罗是非洲最大城市。","history":"公元前3100年美尼斯统一上下埃及，建立第一王朝。古王国时期建造了胡夫金字塔。公元前332年被亚历山大大帝征服。公元639年阿拉伯人进入，伊斯兰化。1882年被英国占领。1952年纳赛尔领导革命推翻 monarchy，建立共和国。"},
    {"name":"泉州","type":"城市","tag":"中国","desc":"福建省沿海城市，宋元时期世界最大港口之一。2021年\"泉州：宋元中国的世界海洋商贸中心\"列入世界文化遗产。拥有伊斯兰教、基督教、印度教等多种宗教遗迹。","history":"唐代开始成为重要港口。宋元时期达到鼎盛，马可·波罗称之为\"光明之城\"。元朝时意大利商人雅各·德安科纳在此居住。明清海禁后衰落。改革开放后重新成为经济重镇。"},
    {"name":"廷巴克图","type":"城市","tag":"西非","desc":"马里共和国中部城市，历史上是撒哈拉贸易路线上的学术中心。桑科尔大学曾是伊斯兰世界最重要的学府之一。手抄本文化极为发达。","history":"公元5世纪由图阿雷格人建立。14世纪成为马里帝国的文化和商业中心。桑科尔大学鼎盛时期有约2.5万名学生。1591年被摩洛哥军队攻陷，学术中心地位衰落。2012年伊斯兰极端分子破坏古墓和手抄本。"},
    {"name":"斯里兰卡","type":"国家","tag":"南亚","desc":"印度洋上的岛国，被称为\"印度洋的珍珠\"。以红茶、宝石和香料闻名。拥有世界上最古老的佛教文献。1948年独立，2009年结束长达26年的内战。","history":"公元前543年僧伽罗人从北印度迁入。公元前247年佛教传入。16世纪起先后被葡萄牙、荷兰和英国殖民。1948年独立，国名锡兰。1972年改名为斯里兰卡共和国。1983-2009年内战。2022年遭遇严重经济危机。"},
    {"name":"布达佩斯","type":"城市","tag":"中欧","desc":"匈牙利首都，多瑙河畔的\"东欧巴黎\"。由河西的布达和河东的佩斯合并而成。以温泉浴场、国会大厦和链子桥闻名。拥有欧洲最古老的地铁（1896年）。","history":"公元前1世纪罗马人建立阿昆库姆城。896年马扎尔人进入匈牙利平原。1867年奥匈帝国建立，布达佩斯成为双首都之一。1873年布达、佩斯和老布达正式合并。1956年爆发反苏起义，被镇压。2004年匈牙利加入欧盟。"},
    {"name":"秘鲁","type":"国家","tag":"南美洲","desc":"南美洲第三大国家。拥有亚马逊雨林、安第斯山脉和太平洋海岸。马丘比丘是世界上最著名的考古遗址之一。羊驼毛纺织品闻名世界。","history":"公元前3000年卡拉尔文明兴起。15世纪印加帝国以库斯科为中心崛起。1533年西班牙殖民者皮萨罗征服印加帝国。1821年独立。1980-2000年光辉道路游击战导致近7万人死亡。"},
    {"name":"梵蒂冈","type":"国家","tag":"欧洲","desc":"世界上最小的国家，面积0.44平方公里（仅相当于60个足球场）。全球天主教中心，教皇驻地。拥有世界上最大的图书馆之一——梵蒂冈图书馆，藏有180万册古籍。","history":"公元4世纪在圣彼得墓地上建立教堂。756年法兰克国王丕平赠地建立教皇国。1870年意大利统一后教皇国被吞并。1929年拉特兰条约承认梵蒂冈为主权国家。2013年本笃十六世成为600年来首位退位的教皇。"},
]

# 知识卡片库（每天推送3个，轮流）
HISTORY_TERMS = [
    {"term":"年鉴学派","field":"历史学","def":"20世纪法国史学流派，主张\"总体史\"研究，关注长时段的结构性变化，而非传统政治史的事件叙述。代表人物布罗代尔提出\"地理时间、社会时间、事件时间\"三重时间观。"},
    {"term":"全球史","field":"历史学","def":"20世纪后期兴起的史学范式，超越民族国家的分析框架，关注跨区域联系、交流和比较。强调\"连接性\"而非\"特殊性\"，代表著作有麦克尼尔的《西方的兴起》。"},
    {"term":"记忆之场","field":"历史学","def":"法国史学家皮埃尔·诺拉提出的概念，指集体记忆凝聚的符号性场所或事物（如国庆日、纪念碑、档案）。认为现代社会的记忆已经断裂，需要人造的\"记忆之场\"来维系。"},
    {"term":"长时段","field":"历史学","def":"布罗代尔提出的历史时间分层理论中的最深层。关注几乎不变的地理环境、气候、生态因素，以及缓慢变化的思维定势（心态）。认为这才是历史的深层结构。"},
    {"term":"概念史","field":"历史学","def":"研究核心政治和社会概念在历史中的形成与演变的史学方法。德国学者科塞雷克创立，认为概念既是历史变化的指标，也是推动变化的因素。如\"民主\"\"革命\"\"阶级\"等概念的语义变迁。"},
    {"term":"微观史学","field":"历史学","def":"20世纪70年代兴起的史学方法，通过聚焦一个小人物、小事件或小社区来透视宏大的历史结构。意大利史学家金茨堡的《奶酪与蠕虫》是典范之作，讲述16世纪一个磨坊主的世界观。"},
    {"term":"历史叙事主义","field":"历史学","def":"海登·怀特提出的理论，认为历史著作本质上是文学叙事，历史学家通过\"情节化\"（将事件编排成浪漫剧、悲剧、喜剧或讽刺剧）来赋予历史意义。引发\"语言学转向\"的激烈争论。"},
    {"term":"历史记忆","field":"历史学","def":"研究社会如何建构、传承和遗忘集体记忆的领域。不同于客观的历史学，记忆是经过选择和重构的。扬·阿斯曼提出\"文化记忆\"理论，区分交往记忆（三代人）和文化记忆（千年）。"},
    {"term":"核心素养","field":"教育学","def":"学生应具备的必备品格和关键能力，OECD于1997年提出。中国2016年发布《中国学生发展核心素养》，包括文化基础、自主发展、社会参与三大维度，共18个基本要点。"},
    {"term":"最近发展区","field":"教育学","def":"维果茨基提出的学习理论，指学生独立解决问题的实际能力与在他人帮助下可达到的潜在能力之间的差距。教学应着眼于\"跳一跳够得着\"的区域，即最近发展区。"},
    {"term":"脚手架理论","field":"教育学","def":"源自维果茨基最近发展区理论的教学策略。教师提供临时性支持（\"脚手架\"），帮助学生完成超出独立能力的任务。随着学生能力的增长，逐步撤除支持。强调\"适时退出\"。"},
    {"term":"布鲁姆分类学","field":"教育学","def":"1956年本杰明·布鲁姆提出的教育目标分类体系，分为认知、情感、动作技能三大领域。认知领域从低到高六层次：记忆、理解、应用、分析、评价、创造。2001年修订版将\"创造\"提到最高层。"},
   {"term":"建构主义","field":"教育学","def":"学习者不是被动接收知识，而是在已有经验基础上主动建构知识。皮亚杰的认知建构主义和维果茨基的社会建构主义是两大流派。强调情境化、协作式、自主探究的学习方式。"},
    {"term":"元认知","field":"心理学","def":"对自己认知过程的认知和调控的能力。弗拉维尔于1970年代提出。包括元认知知识（知道什么策略有效）和元认知调控（计划、监控、评价）。是区分优秀学习者和普通学习者的关键因素。"},
    {"term":"自我效能感","field":"心理学","def":"班杜拉1977年提出的概念，指个体对自己完成特定任务的能力信念。不同于自信（泛指），自我效能感是具体领域相关的。高自我效能感的人更愿意接受挑战、面对困难更坚持。"},
    {"term":"成长型思维","field":"心理学","def":"卡罗尔·德韦克提出的概念。认为智力是可以通过努力发展的（成长型思维），而非固定不变的（固定型思维）。成长型思维者更愿意接受挑战，把失败看作成长的机会，而非能力的否定。"},
    {"term":"认知负荷","field":"心理学","def":"约翰·斯威勒提出的理论，指工作记忆处理信息时的负担。分为内在认知负荷（任务本身的难度）、外在认知负荷（教学设计不当造成的负担）和相关认知负荷（促进图式建构的加工）。教学应减少外在负荷。"},
    {"term":"刻意练习","field":"心理学","def":"安德斯·埃里克森提出的技能提升方法。不同于普通重复，刻意练习需要明确的目���、即时反馈和适度的挑战。大多数领域的顶尖人才都经历了约1万小时的刻意练习（\"一万小时定律\"）。"},
]

# 书籍推荐库
BOOKS = [
    {"title":"《历史学是什么》","author":"葛剑雄","why":"了解历史学本质的最佳入门书。历史不仅有事实，更有解释和立场。适合准教师理解历史学科的本质。"},
    {"title":"《全球通史》","author":"斯塔夫里阿诺斯","why":"全球史观的经典之作，打破了以西方为中心的历史叙述。从1500年前后的人类迁徙讲到当代全球化。"},
    {"title":"《奶酪与蠕虫》","author":"卡洛·金茨堡","why":"微观史学代表作。通过16世纪一个意大利磨坊主的宇宙观，折射出精英文化与民间文化的碰撞。叙事精彩如小说。"},
    {"title":"《记忆之场》","author":"皮埃尔·诺拉","why":"理解\"历史记忆\"概念的必读书。分析法国人如何通过国旗、国庆、先贤祠等符号构建集体记忆。"},
    {"title":"《历史研究》","author":"汤因比","why":"挑战了\"西方中心论\"的鸿篇巨制。比较分析了21种文明的兴衰，提出\"挑战-应战\"模式解释文明演进。"},
    {"title":"《万历十五年》","author":"黄仁宇","why":"以大历史观写明代一个平淡年份，却揭示了整个帝国体制的结构性困境。叙事手法独特，既是学术著作也是畅销书。"},
    {"title":"《教学勇气》","author":"帕克·帕尔默","why":"不仅仅是教学技巧，更探讨教师的内在心灵。\"好的教学不能降低到技术层面，好的教学来自教师的自我认同与完整。\""},
    {"title":"《教育的目的》","author":"怀特海","why":"怀特海的教育哲学经典。\"学生是有血有肉的人，教育的目的是激发和引导他们的自我发展。\"反对灌输死知识。"},
    {"title":"《学会提问》","author":"尼尔·布朗","why":"批判性思维训练经典。教人区分事实与观点、识别逻辑谬误、评估证据质量。对历史教师培养学生的历史思维能力极有帮助。"},
    {"title":"《枪炮、病菌与钢铁》","author":"贾雷德·戴蒙德","why":"从地理和环境角度解释世界各大洲发展差异。为什么欧亚大陆征服了美洲而非相反？对人类文明史提出了颠覆性的宏观解释。"},
    {"title":"《思考，快与慢》","author":"丹尼尔·卡尼曼","why":"诺贝尔经济学奖得主的毕生研究。揭示人类思维的两种系统：快速直觉的系统1和缓慢理性的系统2。理解认知偏差有助于教学设计。"},
    {"title":"《民主主义与教育》","author":"约翰·杜威","why":"实用主义教育学的奠基之作。教育即生活，学校即社会。\"教育是经验的重组和改造\"。对理解现代教育理念至关重要。"},
    {"title":"《丝绸之路》","author":"彼得·弗兰科潘","why":"以丝绸之路为轴心重写世界史，颠覆了以地中海为中心的传统视角。从中亚视角看2000年来信仰、战争、贸易和疾病的全球流动。"},
    {"title":"《第三帝国的语言》","author":"维克多·克莱普勒","why":"一位犹太语言学家在纳粹统治期间的语言笔记。记录语言如何被政治扭曲和毒化。对理解历史语境下的语言教育极具启发性。"},
]

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
            if not ti or ti.lower() in seen: continue
            seen.add(ti.lower())
            de = it.find("description") or it.find(f"{ns}summary") or it.find("summary")
            ds = ""
            if de is not None:
                ds = de.text or "".join(de.itertext()) or ""
                ds = re.sub(r"<[^>]+>", "", ds).strip()[:300]
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
log(f"共 {len(art)} 篇")

# 每天选不同的地区和知识卡（基于日期）
day_num = datetime.now().timetuple().tm_yday
region = REGIONS[day_num % len(REGIONS)]
h_term1 = HISTORY_TERMS[(day_num * 3) % len(HISTORY_TERMS)]
h_term2 = HISTORY_TERMS[(day_num * 3 + 1) % len(HISTORY_TERMS)]
h_term3 = HISTORY_TERMS[(day_num * 3 + 2) % len(HISTORY_TERMS)]
book = BOOKS[day_num % len(BOOKS)]

os.makedirs(DIR, exist_ok=True)

# === 生成HTML ===
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"Noto Sans SC",sans-serif;background:#f5f0eb;color:#2c1810;line-height:1.6}
a{color:#2d6a4f;text-decoration:none}
a:hover{text-decoration:underline}
nav{background:#2d6a4f;padding:10px 16px;color:#fff;text-align:center;font-size:16px;font-weight:700}
.c{max-width:800px;margin:0 auto;padding:16px}
h2{font-size:18px;color:#2d6a4f;margin:20px 0 10px;border-bottom:2px solid #2d6a4f;padding-bottom:4px}
.card{background:#fff;border-radius:8px;padding:12px 14px;margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,.06);border-left:3px solid #2d6a4f}
.card .m{font-size:11px;color:#888;margin-bottom:4px}
.card .en{font-size:13px;color:#666;font-style:italic;margin-bottom:2px}
.card .cn{font-size:14px;color:#2c1810;font-weight:600}
.region-box{background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-radius:10px;padding:16px;margin-bottom:12px}
.region-box .name{font-size:20px;font-weight:700;color:#1b5e20}
.region-box .tag{display:inline-block;background:#2d6a4f;color:#fff;padding:2px 10px;border-radius:10px;font-size:11px;margin:4px 0}
.region-box .desc{font-size:13px;color:#333;margin:6px 0}
.region-box .history{font-size:12px;color:#555;margin-top:6px;line-height:1.6}
.knowledge-box{background:#fff;border-radius:10px;padding:14px;margin-bottom:8px;border-left:3px solid #1565c0}
.knowledge-box .term{font-size:15px;font-weight:700;color:#1565c0}
.knowledge-box .field{font-size:11px;color:#888;margin:2px 0}
.knowledge-box .def{font-size:13px;color:#444;margin-top:4px;line-height:1.6}
.book-box{background:#fff3e0;border-radius:10px;padding:14px;margin-bottom:12px;border-left:3px solid #e65100}
.book-box .title{font-size:15px;font-weight:700;color:#e65100}
.book-box .author{font-size:12px;color:#888}
.book-box .why{font-size:13px;color:#444;margin-top:4px;line-height:1.6}
.f{text-align:center;padding:20px;color:#888;font-size:12px;border-top:1px solid #ddd;margin-top:30px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:8px}
"""

def cd(a):
    dt = f"<span>{a['date']}</span>" if a["date"] else ""
    return f"<div class='card'><div class='m'>{esc(a['src'])} ⭐{a['sc']} {dt}</div><div class='en'>{esc(a['title'])}</div><div class='cn'>{esc(a.get('title_cn',''))}</div></div>"

def pg(body):
    return f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>历史教育学·每日简报</title><style>{CSS}</style></head><body><nav>🎓 历史教育学 · 每日简报</nav><div class='c'>{body}</div><div class='f'>每日更新 · 历史教育学 · 全球视野</div></body></html>"

log("生成HTML...")

# 今日地区
region_html = f"<div class='region-box'><div class='name'>🌍 {region['name']}</div><div><span class='tag'>{region['type']}</span><span class='tag'>{region['tag']}</span></div><div class='desc'>{esc(region['desc'])}</div><div class='history'><strong>📜 历史概览：</strong>{esc(region['history'])}</div></div>"

# 知识卡
k1 = f"<div class='knowledge-box'><div class='term'>📌 {esc(h_term1['term'])}</div><div class='field'>{esc(h_term1['field'])}</div><div class='def'>{esc(h_term1['def'])}</div></div>"
k2 = f"<div class='knowledge-box'><div class='term'>📌 {esc(h_term2['term'])}</div><div class='field'>{esc(h_term2['field'])}</div><div class='def'>{esc(h_term2['def'])}</div></div>"
k3 = f"<div class='knowledge-box'><div class='term'>📌 {esc(h_term3['term'])}</div><div class='field'>{esc(h_term3['field'])}</div><div class='def'>{esc(h_term3['def'])}</div></div>"

# 书籍推荐
book_html = f"<div class='book-box'><div class='title'>📖 {esc(book['title'])}</div><div class='author'>{esc(book['author'])}</div><div class='why'><strong>推荐理由：</strong>{esc(book['why'])}</div></div>"

articles_html = "<div class='g'>" + "".join(cd(a) for a in art[:8]) + "</div>"

body = f"<h2>📰 今日热点</h2>{articles_html}<h2>🌍 认识一个地方</h2>{region_html}<h2>📖 书籍推荐</h2>{book_html}<h2>📌 今日知识卡</h2>{k1}{k2}{k3}"

open(os.path.join(DIR,"index.html"),"w",encoding="utf-8").write(pg(body))
log("页面生成完成")

# === 部署 ===
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

# === 推送 ===
log("推送微信...")
today = datetime.now().strftime("%Y-%m-%d")
msg = f"<h2 style='color:#2d6a4f;text-align:center'>🎓 历史教育学 · 每日简报</h2><p style='text-align:center;color:#888;font-size:13px'>{today}</p><hr style='border:none;border-top:2px solid #2d6a4f;margin:10px 0'>"

# 文章
if art:
    msg += "<h3 style='color:#2d6a4f'>📰 今日热点</h3>"
    for a in art[:3]:
        msg += f"<div style='margin:6px 0;padding:8px 10px;background:#f0f7f0;border-radius:6px;border-left:3px solid #2d6a4f'><div style='font-size:11px;color:#888'>{esc(a['src'])} ⭐{a['sc']}</div><div style='font-size:13px;color:#666;font-style:italic'>{esc(a['title'])}</div><div style='font-size:14px;color:#2c1810;font-weight:600'>{esc(a.get('title_cn',''))}</div></div>"

# 地区
msg += f"<h3 style='color:#2d6a4f'>🌍 认识一个地方：{esc(region['name'])}</h3><div style='margin:6px 0;padding:10px;background:#e8f5e9;border-radius:6px'><p style='font-size:13px;color:#333'>{esc(region['desc'])}</p></div>"

# 知识卡
msg += f"<h3 style='color:#2d6a4f'>📌 今日知识卡</h3>"
for t in [h_term1, h_term2, h_term3]:
    msg += f"<div style='margin:4px 0;padding:8px 10px;background:#e3f2fd;border-radius:6px;border-left:3px solid #1565c0'><strong style='color:#1565c0;font-size:13px'>{esc(t['term'])}</strong><span style='color:#888;font-size:11px'> · {esc(t['field'])}</span><p style='font-size:12px;color:#444;margin-top:2px'>{esc(t['def'][:120])}</p></div>"

# 书籍
msg += f"<h3 style='color:#2d6a4f'>📖 今日推荐</h3><div style='margin:6px 0;padding:10px;background:#fff3e0;border-radius:6px;border-left:3px solid #e65100'><strong style='color:#e65100'>{esc(book['title'])}</strong><span style='color:#888'> - {esc(book['author'])}</span><p style='font-size:12px;color:#444;margin-top:4px'>{esc(book['why'])}</p></div>"

msg += f"<hr style='border:none;border-top:1px solid #ddd;margin:10px 0'><p style='text-align:center'><a href='{URL}' style='display:inline-block;background:#2d6a4f;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-size:14px'>🌐 查看完整网站</a></p><p style='text-align:center;color:#aaa;font-size:11px;margin-top:6px'>每日更新 · 充实你的知识储备</p>"

b = json.dumps({"token":PUSH,"title":f"🎓历史教育学 {today}","content":msg,"template":"html"}).encode()
r = urllib.request.Request("https://www.pushplus.plus/send",data=b,headers={"Content-Type":"application/json"})
try:
    rp = json.loads(urllib.request.urlopen(r,timeout=10).read())
    if rp.get("code")==200: log("✔推送成功")
    else: log(f"✖{rp}")
except Exception as e: log(f"✖{e}")

print(f"\n==== 完成 ====\n  文章: {len(art)}篇\n  推送: 微信")
