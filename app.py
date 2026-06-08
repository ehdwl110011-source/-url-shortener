from flask import Flask, redirect, request, jsonify, render_template_string
import sqlite3, random, string, os

app = Flask(__name__)
DB_PATH = 'urls.db'
TELEGRAM_URL = 'https://t.me/+0wsZAVlDft80M2Q1'

# 미리보기 정보
OG_TITLE = '이럴때일수록 잃지않는법'
OG_DESC = '혼자가 아닙니다'
OG_IMAGE = 'https://i.ibb.co/ycmjZXPS/image.png'

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS urls (
            code TEXT PRIMARY KEY,
            target TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

def make_code(n=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=n))
        with db() as c:
            if not c.execute('SELECT 1 FROM urls WHERE code=?', (code,)).fetchone():
                return code

PAGE = '''
<!DOCTYPE html><html><head><meta charset="utf-8"><title>관리자</title>
<style>
body{font-family:sans-serif;max-width:600px;margin:40px auto;padding:20px;background:#f5f5f5}
h1{color:#333}input,select,button{padding:10px;margin:5px;font-size:14px}
input{width:60%}button{background:#03c75a;color:#fff;border:0;cursor:pointer;border-radius:4px}
.item{background:#fff;padding:10px;margin:5px 0;border-radius:4px;display:flex;justify-content:space-between}
.code{color:#03c75a;font-weight:bold}.del{background:#e74c3c;color:#fff;border:0;padding:5px 10px;cursor:pointer;border-radius:4px}
</style></head><body>
<h1>🔗 단축 URL 관리</h1>
<div>
  <input id="url" placeholder="긴 주소 입력 (https://...)">
  <select id="dst"><option value="web">웹으로 열기</option><option value="nmap">네이버 지도 앱</option></select>
  <button onclick="create()">짧은 주소 만들기</button>
</div>
<h3>📋 저장된 주소</h3>
<div id="list"></div>
<script>
async function create(){
  const url=document.getElementById('url').value;
  if(!url){alert('주소를 입력하세요');return}
  const dst=document.getElementById('dst').value;
  const r=await fetch('/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url,dst})});
  const d=await r.json();
  alert('짧은 주소: '+d.short);
  document.getElementById('url').value='';
  load();
}
async function load(){
  const r=await fetch('/list');const list=await r.json();
  document.getElementById('list').innerHTML=list.map(x=>
    `<div class="item"><div><a href="/${x.code}" target="_blank" class="code">/${x.code}</a> → ${x.target.substring(0,50)}... (클릭 ${x.clicks}회)</div>
    <button class="del" onclick="del('${x.code}')">삭제</button></div>`).join('')||'<p>아직 없음</p>';
}
async function del(code){
  if(!confirm('삭제?'))return;
  await fetch('/delete/'+code,{method:'DELETE'});load();
}
load();
</script></body></html>
'''

@app.route('/')
def home():
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{OG_TITLE}</title>
<meta property="og:type" content="website">
<meta property="og:title" content="{OG_TITLE}">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:url" content="https://url-shortener-kn6p.onrender.com">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{OG_TITLE}">
<meta name="twitter:description" content="{OG_DESC}">
<meta name="twitter:image" content="{OG_IMAGE}">
<meta http-equiv="refresh" content="0; url={TELEGRAM_URL}">
<script>window.location.href="{TELEGRAM_URL}";</script>
</head>
<body style="font-family:sans-serif;text-align:center;padding-top:80px;background:#f5f5f5">
<h2>{OG_TITLE}</h2>
<p>{OG_DESC}</p>
<p style="color:gray">잠시만 기다려주세요...</p>
<p><a href="{TELEGRAM_URL}">자동으로 이동하지 않으면 클릭</a></p>
</body>
</html>'''
    return html

@app.route('/admin')
def admin():
    return render_template_string(PAGE)

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    url, dst = data['url'], data.get('dst', 'web')
    code = make_code()
    base = request.host_url.rstrip('/')
    target = f'{base}/bridge?dst={dst}&url={url}'
    with db() as c:
        c.execute('INSERT INTO urls (code, target) VALUES (?, ?)', (code, target))
    return jsonify({'short': f'{base}/{code}', 'code': code})

@app.route('/list')
def list_urls():
    with db() as c:
        rows = c.execute('SELECT code, target, clicks FROM urls ORDER BY created_at DESC').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/delete/<code>', methods=['DELETE'])
def delete(code):
    with db() as c:
        c.execute('DELETE FROM urls WHERE code=?', (code,))
    return jsonify({'ok': True})

@app.route('/bridge')
def bridge():
    dst = request.args.get('dst', 'web')
    url = request.args.get('url', 'https://www.google.com')
    return f'''
<!DOCTYPE html><html><head><meta charset="utf-8"><title>이동 중...</title>
<style>body{{font-family:sans-serif;text-align:center;padding-top:80px;background:#f5f5f5}}
.count{{font-size:60px;color:#03c75a;font-weight:bold}}</style></head><body>
<h2>잠시만 기다려주세요</h2>
<div class="count" id="c">1</div>
<p style="color:gray">목적지: {dst}</p>
<script>
const dst="{dst}",url="{url}";
const ua=navigator.userAgent;
const isAndroid=/Android/.test(ua),isIOS=/iPhone|iPad|iPod/.test(ua);
let n=1;
const t=setInterval(()=>{{
  n--;document.getElementById('c').textContent=n;
  if(n<=0){{
    clearInterval(t);
    if(dst==="nmap"){{
      if(isAndroid){{location.href="intent://"+url.replace(/^https?:\\/\\//,"")+"#Intent;scheme=https;package=com.nhn.android.nmap;end"}}
      else if(isIOS){{location.href="nmap://";setTimeout(()=>location.href=url,1500)}}
      else{{location.href=url}}
    }} else {{location.href=url}}
  }}
}},500);
</script></body></html>
'''

@app.route('/<code>')
def go(code):
    with db() as c:
        row = c.execute('SELECT target FROM urls WHERE code=?', (code,)).fetchone()
        if not row:
            return '그런 주소는 없어요!', 404
        c.execute('UPDATE urls SET clicks=clicks+1 WHERE code=?', (code,))
        return redirect(row['target'], code=302)

init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
