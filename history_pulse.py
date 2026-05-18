# -*- coding: utf-8 -*-
import sys, os, json, re, base64, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict

TOKEN = os.environ.get("GH_TOKEN", "")
PUSH = os.environ.get("PUSH_TOKEN", "")
USER = "xhy0911"
REPO = "history-pulse"
URL = f"https://{USER}.github.io/{REPO}/"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_site")
AKW = ["teacher","teaching","classroom","curriculum","education","student","pedagogy","lesson","school","assessment","learning","textbook","instruction","course","class","worksheet","facts","worksheets","resource","sqa","gcse","alevel"]

SRC = [("Nature-History","https://www.nature.com/subjects/history.rss","CSSCI"),("Smithsonian","https://www.smithsonianmag.com/rss/history/","核心"),("JSTOR Daily","https://daily.jstor.org/feed/","核心"),("Medievalists","https://www.medievalists.net/feed/","普通"),("Ars Technica","https://feeds.arstechnica.com/arstechnica/science","普通"),("School History","https://schoolhistory.co.uk/feed/","普通")]

def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")
def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')
def cls(t,d):
    tt=(t+" "+d).lower()
    return "edu" if any(k in tt for k in AKW) else "hist"

log("抓取RSS...")
art=[]
seen=set()
for nm,url,lv in SRC:
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=12)
        txt=r.read().decode("utf-8",errors="replace")
        rt=ET.fromstring(txt)
        ns=""
        if rt.tag=="{http://www.w3.org/2005/Atom}feed":
            ns="{http://www.w3.org/2005/Atom}"
        its=rt.findall(".//item") or rt.findall(f".//{ns}entry")
        for it in its[:5]:
            t=(it.find("title") or it.find(f"{ns}title"))
            ti=t.text.strip() if t is not None and t.text else ""
            if not ti or ti.lower() in seen: continue
            seen.add(ti.lower())
            de=it.find("description") or it.find(f"{ns}summary") or it.find("summary")
            ds=""
            if de is not None:
                ds=de.text or "".join(de.itertext()) or ""
                ds=re.sub(r"<[^>]+>","",ds).strip()[:200]
            lk=""
            l=it.find("link") or it.find(f"{ns}link")
            if l is not None: lk=l.get("href","") or l.text or ""
            dt=""
            for p in ["pubDate",f"{ns}published",f"{ns}updated"]:
                e=it.find(p)
                if e is not None and e.text:
                    dd=e.text.strip()[:10]
                    if re.match(r"\d{4}-\d{2}-\d{2}",dd): dt=dd; break
            sc=round(5.0+{"CSSCI":2.5,"核心":1.5,"普通":0.5}.get(lv,0.5)+(1.0 if len(ti)>40 else 0),1)
            art.append({"id":len(art)+1,"title":ti,"src":nm,"lv":lv,"sc":min(10,sc),"date":dt,"desc":ds,"link":lk,"cat":cls(ti,ds)})
    except:
        pass
    log(f"  {nm}")

art.sort(key=lambda a:-a["sc"])
log(f"共 {len(art)} 篇")
os.makedirs(DIR,exist_ok=True)

# === HTML ===
CSS="""
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
h1{font-size:22px;color:#2c1810;margin-bottom:16px}
h2{font-size:17px;border-bottom:2px solid #dccfc4;padding-bottom:6px;margin:20px 0 12px}
.card{background:#fff;border-radius:8px;padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.card .m{font-size:12px;color:#9a7a5e;margin-bottom:4px;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.card h3{font-size:15px;margin-bottom:4px}
.card .d{font-size:13px;color:#666;margin-top:4px}
.tg{display:inline-block;padding:1px 7px;border-radius:6px;font-size:11px;font-weight:600}
.c1{background:#1a3a5c;color:#fff}
.c2{background:#8b4513;color:#fff}
.c3{background:#c4a882;color:#fff}
.gr{background:#2d6a4f;color:#fff}
.sc{color:#e67e22;font-weight:600}
.f{text-align:center;padding:24px;color:#9a7a5e;font-size:12px;border-top:1px solid #dccfc4;margin-top:30px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
@media(max-width:600px){.g{grid-template-columns:1fr}}
"""

def nv(cur):
    p=[("index.html","首页"),("history.html","历史学"),("education.html","教育"),("daily.html","每日")]
    n=""
    for path,label in p:
        if cur==path: n+=f"<a href='{path}' style='background:rgba(255,255,255,.15);color:#fff'>{label}</a>"
        else: n+=f"<a href='{path}'>{label}</a>"
    return f"<nav><div class='i'><span class='b'>\U0001f30d</span>{n}</div></nav>"

def cd(a):
    lc={"CSSCI":"c1","核心":"c2","普通":"c3"}.get(a["lv"],"c3")
    cc="gr" if a["cat"]=="edu" else "c1"
    ic="\U0001f393" if a["cat"]=="edu" else "\U0001f4dc"
    dt=f"<span>\U0001f4c5 {a['date']}</span>" if a["date"] else ""
    dd=f"<div class='d'>{esc(a['desc'][:100])}</div>" if a["desc"] else ""
    return f"<div class='card'><div class='m'><span class='tg {cc}'>{ic}</span><span class='tg {lc}'>{a['lv']}</span><span class='sc'>\u2b50{a['sc']}</span><span>{esc(a['src'])}</span>{dt}</div><h3><a href='article_{a['id']}.html'>{esc(a['title'])}</a></h3>{dd}</div>"

def pg(title,body,cur):
    return f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>{esc(title)}</title><style>{CSS}</style></head><body>{nv(cur)}<div class='c'>{body}</div><div class='f'><a href='{URL}'>\U0001f310手机版</a> \u00b7 每日更新</div></body></html>"

log("生成HTML...")
h=[a for a in art if a["cat"]=="hist"]
e=[a for a in art if a["cat"]=="edu"]

hero=f"<div style='background:linear-gradient(135deg,#1a0f0a,#3d2a1a);color:#f5e6cc;padding:36px 28px;border-radius:12px;margin-bottom:20px;text-align:center'><div style='font-size:32px;font-weight:800'>\U0001f30d WORLD HISTORY PULSE</div><div style='font-size:15px;color:#c4a882;margin:6px 0'>{datetime.now().strftime('%Y-%m-%d')} \u00b7 {len(art)}篇</div><div style='display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:12px'><a href='history.html' style='padding:8px 20px;background:#8b4513;color:#fff;border-radius:6px'>\U0001f4dc历史学({len(h)})</a><a href='education.html' style='padding:8px 20px;background:#2d6a4f;color:#fff;border-radius:6px'>\U0001f393教育({len(e)})</a><a href='daily.html' style='padding:8px 20px;background:#5c3a1a;color:#fff;border-radius:6px'>\U0001f4c5每日</a></div></div>"
bb=hero+"".join(cd(a) for a in art)
open(os.path.join(DIR,"index.html"),"w",encoding="utf-8").write(pg("史海新萃",bb,"index.html"))
bb=f"<h1>\U0001f4dc历史学({len(h)})</h1>"+"".join(cd(a) for a in h)
open(os.path.join(DIR,"history.html"),"w",encoding="utf-8").write(pg("历史学",bb,"history.html"))
bb=f"<h1>\U0001f393历史教育({len(e)})</h1>"+"".join(cd(a) for a in e)
open(os.path.join(DIR,"education.html"),"w",encoding="utf-8").write(pg("历史教育",bb,"education.html"))
dm=defaultdict(list)
for a in art: dm[a["date"] if a["date"] else "-"].append(a)
bb="<h1>\U0001f4c5每日文章</h1>"
for d in sorted(dm.keys(),reverse=True): bb+=f"<h2>{d}({len(dm[d])})</h2>"+"".join(cd(a) for a in dm[d])
open(os.path.join(DIR,"daily.html"),"w",encoding="utf-8").write(pg("每日文章",bb,"daily.html"))
for a in art:
    lc={"CSSCI":"c1","核心":"c2","普通":"c3"}.get(a["lv"],"c3")
    al=f"<a href='index.html' style='background:#8b4513;color:#fff;padding:8px 18px;border-radius:6px;font-size:13px;display:inline-block'>\u2190返回</a>"
    if a["link"]: al+=f"<a href='{esc(a['link'])}' target='_blank' style='background:#1a3a5c;color:#fff;padding:8px 18px;border-radius:6px;font-size:13px;display:inline-block'>\U0001f517查看原文</a>"
    body=f"<div style='max-width:750px'><div style='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px'><span class='tg {lc}'>{a['lv']}</span><span class='sc'>\u2b50{a['sc']}</span><span style='font-size:13px;color:#9a7a5e'>{esc(a['src'])}</span><span style='font-size:13px;color:#9a7a5e'>('📅 '+a['date'] if a['date'] else '')</span></div><h1 style='font-size:24px;margin:12px 0 16px'>{esc(a['title'])}</h1><div style='background:#faf8f5;padding:20px;border-radius:8px;border-left:3px solid #8b4513;font-size:14px;line-height:1.8;color:#444'>{esc(a['desc'])}</div><div style='margin-top:24px'>{al}</div></div>"
    open(os.path.join(DIR,f"article_{a['id']}.html"),"w",encoding="utf-8").write(pg(a["title"],body,""))
log(f"{len(art)+4}页")

# === DEPLOY ===
log("部署到GitHub...")
HDRS={"Authorization":"token "+TOKEN,"Accept":"application/vnd.github.v3+json"}
def sha(p):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/{USER}/{REPO}/contents/{p}",headers=HDRS),timeout=10).read()).get("sha")
    except: return None
def up(p,c):
    s=sha(p)
    b={"message":"auto "+datetime.now().strftime("%Y-%m-%d"),"content":base64.b64encode(c).decode(),"branch":"main"}
    if s: b["sha"]=s
    r=urllib.request.Request(f"https://api.github.com/repos/{USER}/{REPO}/contents/{p}",data=json.dumps(b).encode(),headers=HDRS,method="PUT")
    r.add_header("Content-Type","application/json")
    try: urllib.request.urlopen(r,timeout=30); return True
    except: return False

fl=[f for f in os.listdir(DIR) if f.endswith(".html") or f=="articles.json"]
ok=0
for f in fl:
    with open(os.path.join(DIR,f),"rb") as fh: c=fh.read()
    if up(f,c): ok+=1
log(f"上传 {ok}/{len(fl)}")

# === PUSH ===
log("推送微信...")
today=datetime.now().strftime("%Y-%m-%d")
msg=f"<h2 style='color:#8b4513;text-align:center'>\U0001f30d 史海新萃</h2><p style='text-align:center;color:#888;font-size:13px'>{today} \u00b7 {len(art)}篇</p><p style='text-align:center'><a href='{URL}' style='display:inline-block;background:#8b4513;color:#fff;padding:8px 20px;border-radius:6px;text-decoration:none;font-size:14px;margin:4px'>\U0001f310 打开完整网站</a></p><hr style='border:none;border-top:2px solid #8b4513;margin:12px 0'>"
for a in art[:8]:
    ic="\U0001f393" if a["cat"]=="edu" else "\U0001f4dc"
    lt={"CSSCI":"<span style='background:#1a3a5c;color:#fff;padding:1px 6px;border-radius:4px;font-size:10px'>CSSCI</span>","核心":"<span style='background:#8b4513;color:#fff;padding:1px 6px;border-radius:4px;font-size:10px'>核心</span>","普通":"<span style='background:#c4a882;color:#fff;padding:1px 6px;border-radius:4px;font-size:10px'>普通</span>"}.get(a["lv"],"")
    msg+=f"<div style='margin:8px 0;padding:10px 12px;background:#faf8f5;border-radius:8px;border-left:3px solid #8b4513'><div style='font-size:11px;color:#888;margin-bottom:4px'>{ic} {esc(a['src'])} {lt} \u2b50{a['sc']}</div><div style='font-size:14px;line-height:1.5'>{esc(a['title'])}</div>"
    if a["desc"]: msg+=f"<div style='font-size:12px;color:#666;margin-top:4px'>{esc(a['desc'][:80])}</div>"
    msg+="</div>"
msg+=f"<hr style='border:none;border-top:1px solid #ddd;margin:12px 0'><p style='text-align:center'><a href='{URL}' style='display:inline-block;background:#8b4513;color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-size:15px'>\U0001f310 点此查看完整网站</a></p><p style='text-align:center;color:#aaa;font-size:12px;margin-top:8px'>每日更新 \u00b7 RSS学术源</p>"
b=json.dumps({"token":PUSH,"title":f"\U0001f30d史海新萃 {today}","content":msg,"template":"html"}).encode()
r=urllib.request.Request("https://www.pushplus.plus/send",data=b,headers={"Content-Type":"application/json"})
try:
    rp=json.loads(urllib.request.urlopen(r,timeout=10).read())
    if rp.get("code")==200: log("\u2714推送成功")
    else: log(f"\u2716{rp}")
except Exception as e: log(f"\u2716{e}")

print(f"\n==== 全部完成 ====")
print(f"  网站: {URL}")
print(f"  文章: {len(art)}篇")
print(f"  推送: 微信")

