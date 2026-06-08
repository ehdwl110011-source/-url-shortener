from flask import Flask, redirect, request
import sqlite3
import random
import string

app = Flask(__name__)
DB_PATH = "urls.db"


# ===== DB 함수들 =====
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            code TEXT PRIMARY KEY,
            target TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # 기존 DB에 clicks 컬럼이 없을 수도 있어서 안전하게 추가 시도
    try:
        c.execute("ALTER TABLE urls ADD COLUMN clicks INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # 이미 있으면 무시
    conn.commit()
    conn.close()
    print("DB 준비 완료!")


def get_url(code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT target FROM urls WHERE code = ?", (code,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def save_url(code, target):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO urls (code, target) VALUES (?, ?)", (code, target))
    conn.commit()
    conn.close()


def delete_url(code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM urls WHERE code = ?", (code,))
    conn.commit()
    conn.close()


def increment_clicks(code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()


def code_exists(code):
    return get_url(code) is not None


def make_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if not code_exists(code):
            return code


# ===== 라우트 =====

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>나만의 단축 URL</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    :root {
      --bg: #f8f9fb;
      --card-bg: #ffffff;
      --text: #1a1a1a;
      --text-light: #6b7280;
      --primary: #6366f1;
      --primary-dark: #4f46e5;
      --border: #e5e7eb;
      --hover: #f3f4f6;
      --success: #10b981;
      --danger: #ef4444;
    }
    
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #0f172a;
        --card-bg: #1e293b;
        --text: #f1f5f9;
        --text-light: #94a3b8;
        --primary: #818cf8;
        --primary-dark: #6366f1;
        --border: #334155;
        --hover: #334155;
      }
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Pretendard", sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 40px 20px;
      transition: background 0.3s;
    }
    
    .container {
      max-width: 640px;
      margin: 0 auto;
    }
    
    .header {
      text-align: center;
      margin-bottom: 40px;
    }
    
    .header h1 {
      font-size: 36px;
      font-weight: 800;
      background: linear-gradient(135deg, #6366f1, #a855f7);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }
    
    .header p {
      color: var(--text-light);
      font-size: 15px;
    }
    
    .card {
      background: var(--card-bg);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.08);
      border: 1px solid var(--border);
      margin-bottom: 24px;
    }
    
    .input-group { margin-bottom: 12px; }
    
    input[type=text], select {
      width: 100%;
      padding: 14px 16px;
      font-size: 15px;
      border: 1.5px solid var(--border);
      border-radius: 10px;
      background: var(--card-bg);
      color: var(--text);
      transition: all 0.2s;
      font-family: inherit;
    }
    
    input[type=text]:focus, select:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 4px rgba(99,102,241,0.1);
    }
    
    button {
      width: 100%;
      padding: 14px 20px;
      font-size: 15px;
      font-weight: 600;
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: white;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: transform 0.1s, box-shadow 0.2s;
      font-family: inherit;
    }
    
    button:hover { box-shadow: 0 6px 20px rgba(99,102,241,0.4); }
    button:active { transform: scale(0.98); }
    button:disabled { opacity: 0.6; cursor: not-allowed; }
    
    .spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
      vertical-align: middle;
      margin-right: 8px;
    }
    
    @keyframes spin { to { transform: rotate(360deg); } }
    
    #result {
      margin-top: 16px;
      padding: 16px;
      background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.1));
      border-radius: 10px;
      display: none;
      animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    #result .label {
      font-size: 13px;
      color: var(--text-light);
      margin-bottom: 6px;
    }
    
    #result .url-row {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    
    #result a {
      flex: 1;
      color: var(--primary);
      font-weight: 600;
      font-size: 16px;
      word-break: break-all;
      text-decoration: none;
    }
    
    #result a:hover { text-decoration: underline; }
    
    .copy-btn {
      padding: 8px 14px;
      width: auto;
      font-size: 13px;
      background: var(--card-bg);
      color: var(--text);
      border: 1px solid var(--border);
    }
    
    .copy-btn:hover {
      background: var(--hover);
      box-shadow: none;
    }
    
    .copy-btn.copied {
      background: var(--success);
      color: white;
      border-color: var(--success);
    }
    
    .list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    
    .list-header h2 {
      font-size: 18px;
      font-weight: 700;
    }
    
    .list-count {
      font-size: 13px;
      color: var(--text-light);
      background: var(--hover);
      padding: 4px 10px;
      border-radius: 999px;
    }
    
    .url-item {
      padding: 14px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      margin-bottom: 8px;
      transition: all 0.2s;
    }
    
    .url-item:hover {
      transform: translateX(2px);
      border-color: var(--primary);
    }
    
    .url-item-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    
    .url-item a {
      color: var(--primary);
      font-weight: 600;
      text-decoration: none;
      font-size: 14px;
    }
    
    .url-item a:hover { text-decoration: underline; }
    
    .url-item .target {
      font-size: 12px;
      color: var(--text-light);
      word-break: break-all;
    }
    
    .url-item-bottom {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
    }
    
    .clicks-badge {
      font-size: 12px;
      color: var(--text-light);
    }
    
    .delete-btn {
      background: transparent;
      color: var(--danger);
      border: none;
      padding: 4px 8px;
      width: auto;
      font-size: 12px;
      cursor: pointer;
    }
    
    .delete-btn:hover {
      background: rgba(239,68,68,0.1);
      box-shadow: none;
    }
    
    .empty {
      text-align: center;
      padding: 30px;
      color: var(--text-light);
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🔗 나만의 단축 URL</h1>
      <p>긴 주소를 짧고 간편하게</p>
    </div>
    
    <div class="card">
      <div class="input-group">
        <input type="text" id="urlInput" placeholder="https://example.com">
      </div>
      <div class="input-group">
        <select id="dstSelect">
          <option value="web">🌐 웹으로 열기</option>
          <option value="nmap">🗺️ 네이버 지도 앱으로 열기</option>
        </select>
      </div>
      <button id="createBtn" onclick="makeShort()">짧은 주소 만들기</button>
      
      <div id="result"></div>
    </div>
    
    <div class="card">
      <div class="list-header">
        <h2>📋 내가 만든 주소</h2>
        <span class="list-count" id="listCount">0</span>
      </div>
      <div id="urlList"></div>
    </div>
  </div>
  
  <script>
    async function makeShort() {
      const url = document.getElementById('urlInput').value.trim();
      const dst = document.getElementById('dstSelect').value;
      const btn = document.getElementById('createBtn');
      
      if (!url) {
        alert('주소를 입력해주세요!');
        return;
      }
      
      // 로딩 표시
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span>만드는 중...';
      
      try {
        const response = await fetch('/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url, dst })
        });
        const data = await response.json();
        
        const resultDiv = document.getElementById('result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
          <div class="label">✨ 짧은 주소가 만들어졌어요!</div>
          <div class="url-row">
            <a href="${data.short}" target="_blank">${data.short}</a>
            <button class="copy-btn" onclick="copyUrl('${data.short}', this)">복사</button>
          </div>
        `;
        
        document.getElementById('urlInput').value = '';
        loadList();
      } catch (e) {
        alert('오류가 발생했어요: ' + e.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '짧은 주소 만들기';
      }
    }
    
    async function copyUrl(url, btn) {
      try {
        await navigator.clipboard.writeText(url);
        const originalText = btn.innerText;
        btn.innerText = '✓ 복사됨';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.innerText = originalText;
          btn.classList.remove('copied');
        }, 1500);
      } catch (e) {
        alert('복사 실패: ' + e.message);
      }
    }
    
    async function deleteUrl(code) {
      if (!confirm('정말 삭제할까요?')) return;
      await fetch('/delete/' + code, { method: 'DELETE' });
      loadList();
    }
    
    async function loadList() {
      const response = await fetch('/list');
      const data = await response.json();
      
      document.getElementById('listCount').innerText = data.length + '개';
      
      const listDiv = document.getElementById('urlList');
      if (data.length === 0) {
        listDiv.innerHTML = '<div class="empty">아직 만든 게 없어요 ✨</div>';
        return;
      }
      
      listDiv.innerHTML = data.map(item => {
        const shortUrl = window.location.origin + '/' + item.code;
        return `
          <div class="url-item">
            <div class="url-item-top">
              <a href="${shortUrl}" target="_blank">${shortUrl}</a>
              <button class="copy-btn" onclick="copyUrl('${shortUrl}', this)">복사</button>
            </div>
            <div class="target">→ ${item.target}</div>
            <div class="url-item-bottom">
              <span class="clicks-badge">👆 ${item.clicks}회 클릭</span>
              <button class="delete-btn" onclick="deleteUrl('${item.code}')">삭제</button>
            </div>
          </div>
        `;
      }).join('');
    }
    
    // Enter 키로 만들기
    document.getElementById('urlInput').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') makeShort();
    });
    
    loadList();
  </script>
</body>
</html>
    """


@app.route("/create", methods=["POST"])
def create():
    data = request.get_json()
    long_url = data.get("url")
    dst = data.get("dst", "web")
    
    code = make_short_code()
    bridge_url = f"http://127.0.0.1:8000/bridge?dst={dst}&url={long_url}"
    save_url(code, bridge_url)
    
    short_url = f"http://127.0.0.1:5000/{code}"
    print(f"새 짧은 주소: {code} → {long_url}")
    
    return {"short": short_url, "code": code}


@app.route("/list")
def list_urls():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT code, target, clicks FROM urls ORDER BY created_at DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [{"code": r[0], "target": r[1], "clicks": r[2]} for r in rows]


@app.route("/delete/<code>", methods=["DELETE"])
def delete(code):
    delete_url(code)
    return {"ok": True}


@app.route("/<code>")
def go(code):
    target = get_url(code)
    if target:
        increment_clicks(code)  # 클릭 카운트 증가!
        return redirect(target, code=302)
    return "그런 주소는 없어요!", 404


if __name__ == "__main__":
    init_db()
    app.run(port=5000)
