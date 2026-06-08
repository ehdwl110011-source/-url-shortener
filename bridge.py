from flask import Flask, request

app = Flask(__name__)


@app.route("/bridge")
def bridge():
    dst = request.args.get("dst", "web")
    url = request.args.get("url", "https://www.google.com")
    
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>이동 중...</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    :root {{
      --bg: #f8f9fb;
      --card-bg: #ffffff;
      --text: #1a1a1a;
      --text-light: #6b7280;
      --primary: #6366f1;
      --border: #e5e7eb;
    }}
    
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f172a;
        --card-bg: #1e293b;
        --text: #f1f5f9;
        --text-light: #94a3b8;
        --primary: #818cf8;
        --border: #334155;
      }}
    }}
    
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Pretendard", sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    
    .card {{
      background: var(--card-bg);
      border-radius: 20px;
      padding: 48px 32px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.1);
      max-width: 420px;
      width: 100%;
      text-align: center;
      border: 1px solid var(--border);
    }}
    
    .icon-wrap {{
      width: 80px;
      height: 80px;
      margin: 0 auto 24px;
      background: linear-gradient(135deg, #6366f1, #a855f7);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 36px;
      animation: pulse 1.5s ease-in-out infinite;
    }}
    
    @keyframes pulse {{
      0%, 100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(99,102,241,0.4); }}
      50% {{ transform: scale(1.05); box-shadow: 0 0 0 20px rgba(99,102,241,0); }}
    }}
    
    h1 {{
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    
    .countdown {{
      font-size: 48px;
      font-weight: 800;
      color: var(--primary);
      margin: 16px 0;
      font-variant-numeric: tabular-nums;
    }}
    
    .info {{
      color: var(--text-light);
      font-size: 14px;
      margin-top: 12px;
    }}
    
    .url-preview {{
      margin-top: 20px;
      padding: 12px;
      background: var(--bg);
      border-radius: 10px;
      font-size: 13px;
      color: var(--text-light);
      word-break: break-all;
      border: 1px solid var(--border);
    }}
    
    .skip-btn {{
      margin-top: 20px;
      padding: 10px 20px;
      background: transparent;
      color: var(--primary);
      border: 1.5px solid var(--primary);
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-family: inherit;
      font-weight: 600;
      transition: all 0.2s;
    }}
    
    .skip-btn:hover {{
      background: var(--primary);
      color: white;
    }}
    
    .dst-tag {{
      display: inline-block;
      padding: 4px 12px;
      background: rgba(99,102,241,0.1);
      color: var(--primary);
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 8px;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon-wrap">🚀</div>
    <div class="dst-tag">{dst.upper()}</div>
    <h1>잠시만요...</h1>
    <div class="countdown" id="countdown">3</div>
    <div class="info">곧 이동합니다</div>
    <div class="url-preview" id="urlPreview">{url}</div>
    <button class="skip-btn" onclick="goNow()">지금 바로 이동</button>
  </div>
  
  <script>
    const dst = "{dst}";
    const url = "{url}";
    const ua = navigator.userAgent;
    const isIOS = /iPhone|iPad|iPod/.test(ua);
    const isAndroid = /Android/.test(ua);
    
    let count = 3;
    const countEl = document.getElementById('countdown');
    
    function goNow() {{
      if (dst === "nmap") {{
        if (isAndroid) {{
          location.href = "intent://" + url.replace("https://","").replace("http://","") 
            + "#Intent;scheme=https;package=com.nhn.android.nmap;end";
        }} else if (isIOS) {{
          location.href = "nmap://";
          setTimeout(() => location.href = url, 2000);
        }} else {{
          location.href = url;
        }}
      }} else {{
        location.href = url;
      }}
    }}
    
    const timer = setInterval(() => {{
      count--;
      if (count <= 0) {{
        clearInterval(timer);
        countEl.innerText = '0';
        goNow();
      }} else {{
        countEl.innerText = count;
      }}
    }}, 1000);
  </script>
</body>
</html>
    """
    return html


if __name__ == "__main__":
    app.run(port=8000)
