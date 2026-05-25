import sys, os, json, re, base64, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict

TOKEN = os.environ.get("GH_TOKEN", "")
PUSH = os.environ.get("PUSH_TOKEN", "")
USER = "xhy0911"
REPO = "history-pulse"
URL = f"https://{USER}.github.io/{REPO}/"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_site")
AKW = ["history education","history teaching","history curriculum","history teacher","history classroom","history lesson","history instruction","history assessment","history standard","history reform","history policy","history pedagogy","history learning","history student","historical thinking","historical literacy","historical inquiry","historical analysis","historical reasoning","historical understanding","historical knowledge","historical skill","historical competency","historical narrative","historical perspective","historical empathy","historical consciousness","historical memory","historical interpretation","historical evidence","historical source","primary source","secondary source","document analysis","archival research","oral history","public history","digital history","local history","world history","us history","american history","european history","asian history","african history","ancient history","medieval history","modern history","social studies","civics education","citizenship education","heritage education","museum education","cultural heritage","historic preservation","historical association","historical society","history department","history program","history major","history degree","history graduate","history undergraduate","history PhD","history research","history scholarship","history grant","history funding","history conference","history symposium","history workshop","history seminar","history lecture","history course","history class","history textbook","history curriculum","history standard","history framework","history guideline","history assessment","history exam","history test","history quiz","history project","history assignment","history essay","history paper","history thesis","history dissertation","history publication","history journal","history article","history book","history monograph","history review","history criticism","history debate","history controversy","history revision","history interpretation","history perspective","history narrative","history memory","history commemoration","history anniversary","history exhibition","history museum","history archive","history collection","history preservation","history conservation","history restoration","history education policy","history education reform","history education research","history education study","history education report","history education survey","history education analysis","history education trend","history education innovation","history education technology","history education digital","history education online","history education resource","history education material","history education tool","history education strategy","history education approach","history education method","history education practice","history education pedagogy","history education teacher","history education student","history education classroom","history education school","history education curriculum","history education standard","history education assessment","history education funding","history education grant","history education program","history education initiative","history education project","history education development","history education improvement","history education reform","history education change","history education transformation"]

SRC = [("OECD Edu","https://oecdedutoday.com/feed/","核心"),("Hechinger","https://hechingerreport.org/feed/","核心"),("Brookings Edu","https://www.brookings.edu/feed/?topic=education","核心"),("Harvard Ed","https://www.gse.harvard.edu/feed","核心"),("EduNext","https://www.educationnext.org/feed/","核心"),("Education Week","https://www.edweek.org/feed/?topic=teaching","核心"),("TES Global","https://www.tes.com/rss/news.xml","核心"),("Inside Higher Ed","https://www.insidehighered.com/rss/news","核心")]

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
        for it in its[:5]:
            t = (it.find("title") or it.find(f"{ns}title"))
            ti = t.text.strip() if t is not None and t.text else ""
            if not ti or ti.lower() in seen: continue
            seen.add(ti.lower())
            de = it.find("description") or it.find(f"{ns}summary") or it.find("summary")
            ds = ""
            if de is not None:
                ds = de.text or "".join(de.itertext()) or ""
                ds = re.sub(r"<[^>]+>", "", ds).strip()[:200]
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
            # Translate title
            cn_title = translate(ti)
            art.append({"id":len(art)+1,"title":ti,"title_cn":cn_title,"src":nm,"lv":lv,"sc":min(10,sc),"date":dt,"desc":ds,"link":lk,"cat":"edu"})
    except:
        pass
    log(f"  {nm}")

art.sort(key=lambda a:-a["sc"])
log(f"共 {len(art)} 篇")
os.makedirs(DIR, exist_ok=True)

# === HTML ===
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"Noto Sans SC",sans-serif;background:#f5f0eb;color:#2c1810;line-height:1.6}
a{color:#8b4513;text-decoration:none}
a:hover{text-decoration:underline}
nav{background:#2c1810;padding:10px 16px}
nav .i{max-width:900px;margin:0 auto;display:flex;gap:4px;flex-wrap:wrap;align-items:center}
nav a{color:#d4c5b0;font-size:13px;padding:5px 10px;border-radius:4px}
nav a:hover{background:rgba(255,255,255,.1);color:#fff;text-decoration:none}
nav .b{font-size:15px;font-weight:700;color:#f5e6cc;margin-right:10px}
.c{max-width:900px;margin:0 auto;padding:16px}
h1{font-size:22px;color:#2c1810;margin-bottom:16px;text-align:center}
h2{font-size:17px;border-bottom:2px solid #dccfc4;padding-bottom:6px;margin:20px 0 12px;color:#2d6a4f}
.card{background:#fff;border-radius:8px;padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.06);border-left:3px solid #2d6a4f}
.card .m{font-size:12px;color:#9a7a5e;margin-bottom:4px;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.card .en{font-size:14px;color:#444;font-family:Georgia,serif;margin-bottom:2px}
.card .cn{font-size:15px;color:#2c1810;font-weight:600;margin-bottom:4px}
.card .d{font-size:13px;color:#666;margin-top:4px}
.tg{display:inline-block;padding:1px 7px;border-radius:6px;font-size:11px;font-weight:600}
.c1{background:#1a3a5c;color:#fff}
.c2{background:#8b4513;color:#fff}
.c3{background:#c4a882;color:#fff}
.gr{background:#2d6a4f;color:#fff}
.sc{color:#e67e22;font-weight:600}
.f{text-align:center;padding:24px;color:#9a7a5e;font-size:12px;border-top:1px solid #dccfc4;margin-top:30px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}
@media(max-width:600px){.g{grid-template-columns:1fr}}
"""

def nv(cur):
    p = [("index.html","首页")]
    n = ""
    for path, label in p:
        if cur==path: n+=f"<a href='{path}' style='background:rgba(255,255,255,.15);color:#fff'>{label}</a>"
        else: n+=f"<a href='{path}'>{label}</a>"
    return f"<nav><div class='i'><span class='b'>🎓 历史教育学</span>{n}</div></nav>"

def cd(a):
    lc = {"CSSCI":"c1","核心":"c2","普通":"c3"}.get(a["lv"],"c3")
    dt = f"<span>📅 {a['date']}</span>" if a["date"] else ""
    dd = f"<div class='d'>{esc(a['desc'][:120])}</div>" if a["desc"] else ""
    return f"<div class='card'><div class='m'><span class='tg {lc}'>{a['lv']}</span><span class='sc'>⭐{a['sc']}</span><span>{esc(a['src'])}</span>{dt}</div><div class='en'>{esc(a['title'])}</div><div class='cn'>{esc(a.get('title_cn',''))}</div>{dd}</div>"

def pg(title, body, cur):
    return f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>{esc(title)}</title><style>{CSS}</style></head><body>{nv(cur)}<div class='c'>{body}</div><div class='f'><a href='{URL}'>🌐手机版</a> · 每日更新</div></body></html>"

log("生成HTML...")
hero = f"<div style='background:linear-gradient(135deg,#1a3520,#2d6a4f);color:#f5e6cc;padding:36px 28px;border-radius:12px;margin-bottom:20px;text-align:center'><div style='font-size:28px;font-weight:800'>🎓 历史教育学 · 全球教育政策</div><div style='font-size:14px;color:#a8d5ba;margin:6px 0'>{datetime.now().strftime('%Y-%m-%d')} · {len(art)}篇</div></div>"
bb = hero + "<div class='g'>" + "".join(cd(a) for a in art) + "</div>"
open(os.path.join(DIR,"index.html"),"w",encoding="utf-8").write(pg("历史教育学",bb,"index.html"))

# Article details
for a in art:
    lc = {"CSSCI":"c1","核心":"c2","普通":"c3"}.get(a["lv"],"c3")
    al = f"<a href='index.html' style='background:#2d6a4f;color:#fff;padding:8px 18px;border-radius:6px;font-size:13px;display:inline-block'>←返回</a>"
    if a["link"]: al += f"<a href='{esc(a['link'])}' target='_blank' style='background:#1a3a5c;color:#fff;padding:8px 18px;border-radius:6px;font-size:13px;display:inline-block'>🔗查看原文</a>"
    body = f"<div style='max-width:750px'><div style='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px'><span class='tg {lc}'>{a['lv']}</span><span class='sc'>⭐{a['sc']}</span><span style='font-size:13px;color:#9a7a5e'>{esc(a['src'])}</span><span style='font-size:13px;color:#9a7a5e'>{'📅 '+a['date'] if a['date'] else ''}</span></div><div style='font-family:Georgia,serif;font-size:16px;color:#444;margin:12px 0 8px'>{esc(a['title'])}</div><h1 style='font-size:24px;margin:0 0 16px;text-align:left'>{esc(a.get('title_cn',''))}</h1><div style='background:#faf8f5;padding:20px;border-radius:8px;border-left:3px solid #2d6a4f;font-size:14px;line-height:1.8;color:#444'>{esc(a['desc'])}</div><div style='margin-top:24px'>{al}</div></div>"
    open(os.path.join(DIR,f"article_{a['id']}.html"),"w",encoding="utf-8").write(pg(a["title"],body,""))

log(f"{len(art)+1}页")

# === DEPLOY ===
log("部署到GitHub...")
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

# === PUSH ===
log("推送微信...")
today = datetime.now().strftime("%Y-%m-%d")
msg = f"<h2 style='color:#2d6a4f;text-align:center'>🎓 历史教育学 · 全球教育政策</h2><p style='text-align:center;color:#888;font-size:13px'>{today} · {len(art)}篇</p><p style='text-align:center'><a href='{URL}' style='display:inline-block;background:#2d6a4f;color:#fff;padding:8px 20px;border-radius:6px;text-decoration:none;font-size:14px;margin:4px'>🌐 打开完整网站</a></p><hr style='border:none;border-top:2px solid #2d6a4f;margin:12px 0'>"
for a in art[:8]:
    lt = {"CSSCI":"<span style='background:#1a3a5c;color:#fff;padding:1px 6px;border-radius:4px;font-size:10px'>CSSCI</span>","核心":"<span style='background:#8b4513;color:#fff;padding:1px 6px;border-radius:4px;font-size:10px'>核心</span>","普通":"<span style='background:#c4a882;color:#fff;padding:1px 6px;border-radius:4px;font-size:10px'>普通</span>"}.get(a["lv"],"")
    msg += f"<div style='margin:8px 0;padding:10px 12px;background:#f0f7f0;border-radius:8px;border-left:3px solid #2d6a4f'><div style='font-size:11px;color:#888;margin-bottom:4px'>{esc(a['src'])} {lt} ⭐{a['sc']}</div><div style='font-size:13px;color:#666;font-style:italic'>{esc(a['title'])}</div><div style='font-size:14px;color:#2c1810;font-weight:600;margin-top:2px'>{esc(a.get('title_cn',''))}</div>"
    if a["desc"]: msg += f"<div style='font-size:12px;color:#666;margin-top:4px'>{esc(a['desc'][:80])}</div>"
    msg += "</div>"
msg += f"<hr style='border:none;border-top:1px solid #ddd;margin:12px 0'><p style='text-align:center'><a href='{URL}' style='display:inline-block;background:#2d6a4f;color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-size:15px'>🌐 点此查看完整网站</a></p><p style='text-align:center;color:#aaa;font-size:12px;margin-top:8px'>每日更新 · 全球教育政策资讯</p>"
b = json.dumps({"token":PUSH,"title":f"🎓历史教育学 {today}","content":msg,"template":"html"}).encode()
r = urllib.request.Request("https://www.pushplus.plus/send",data=b,headers={"Content-Type":"application/json"})
try:
    rp = json.loads(urllib.request.urlopen(r,timeout=10).read())
    if rp.get("code")==200: log("✔推送成功")
    else: log(f"✖{rp}")
except Exception as e: log(f"✖{e}")

print(f"\n==== 全部完成 ====")
print(f"  网站: {URL}")
print(f"  文章: {len(art)}篇")
print(f"  推送: 微信")
