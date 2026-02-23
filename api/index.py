import requests
import time
from flask import Flask, Response, request, render_template_string
from urllib.parse import urljoin

app = Flask(__name__)
client = requests.Session()

# Global variable to track debug info
debug_info = {
    "last_refresh": "Never",
    "status": "Initializing",
    "using_fallback": False,
    "cookies_found": {}
}

FALLBACK_COOKIE = "Edge-Cache-Cookie=URLPrefix=aHR0cHM6Ly9ibGRjbXByb2QtY2RuLnRvZmZlZWxpdmUuY29t:Expires=1771927793:KeyName=prod_linear:Signature=mmxHt_ttcVgH3693d9c5EIGfVhH34xSHljuGSIipfM1970qE_szW-a3ZRVDNhF9SywWpzUEZ4z1wDUhAOX2sAg"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://toffeelive.com/",
    "Origin": "https://toffeelive.com",
}

CHANNELS = [
    {"name": "Somoy TV", "id": "slang/somoy_tv_320/somoy_tv_320.m3u8?bitrate=768000"},
    {"name": "Jamuna TV HD", "id": "slang/jamuna_tv_576/jamuna_tv_576.m3u8?bitrate=1000000"},
    {"name": "Independent HD", "id": "slang/independent_tv_576/independent_tv_576.m3u8?bitrate=1000000"},
    {"name": "Movie Bangla", "id": "slang/movie_bangla_576/movie_bangla_576.m3u8?bitrate=1000000"},
    {"name": "Sony Sports 1 HD", "id": "sony_sports_1_hd/playlist.m3u8"},
    {"name": "Sony Sports 2 HD", "id": "sony_sports_2_hd/playlist.m3u8"},
    {"name": "Sony Sports 5 HD", "id": "sony_sports_5_hd/playlist.m3u8"},
    {"name": "Ten Cricket", "id": "ten_cricket/playlist.m3u8"},
    {"name": "Sony BBC Earth HD", "id": "sonybbc_earth_hd/playlist.m3u8"},
    {"name": "Sony Yay", "id": "sonyyay/playlist.m3u8"},
    {"name": "Sony Aath", "id": "sonyaath/playlist.m3u8"},
    {"name": "And TV HD", "id": "and_tv_hd/playlist.m3u8"},
    {"name": "Ekhon TV", "id": "ekhon_tv/playlist.m3u8"},
    {"name": "Ekattor TV", "id": "ekattor_tv/playlist.m3u8"},
    {"name": "Toffee Movie", "id": "toffee_movie/playlist.m3u8"},
    {"name": "Nexus TV", "id": "nexus_tv/playlist.m3u8"},
    {"name": "Mohona TV", "id": "mohona_tv/playlist.m3u8"}
]

def refresh_session():
    try:
        client.get("https://toffeelive.com/", headers=BASE_HEADERS, timeout=10)
        debug_info["last_refresh"] = time.strftime('%Y-%m-%d %H:%M:%S')
        ck_dict = client.cookies.get_dict()
        debug_info["cookies_found"] = ck_dict
        
        if 'Edge-Cache-Cookie' in ck_dict:
            debug_info["status"] = "Success (Auto Cookie)"
            debug_info["using_fallback"] = False
        else:
            debug_info["status"] = "Using Fallback (Cookie not found in handshake)"
            debug_info["using_fallback"] = True
    except Exception as e:
        debug_info["status"] = f"Error: {str(e)}"
        debug_info["using_fallback"] = True

@app.route('/')
def home():
    html = """
    <!DOCTYPE html><html><head><title>Mostak Proxy</title><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
    body { font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; max-width: 800px; margin: auto; }
    .card { background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; cursor: pointer; border: 1px solid #334155; }
    .card:hover { border-color: #38bdf8; }
    .copy { color: #38bdf8; font-size: 12px; font-weight: bold; }
    h1 { color: #38bdf8; text-align: center; }
    .debug-link { display: block; text-align: center; color: #94a3b8; margin-top: 20px; text-decoration: none; font-size: 13px; }
    </style></head><body>
    <h1>MOSTAK PROXY</h1>
    <div style="background:#334155; padding:15px; border-radius:8px; margin-bottom:20px; font-family:monospace; font-size:13px;">
    Endpoint: {{ url }}/Mostak?id=ID</div>
    {% for ch in channels %}<div class="card" onclick="copy('{{ ch.id }}')"><span>{{ ch.name }}</span><span class="copy">COPY LINK</span></div>{% endfor %}
    <a href="/debug" class="debug-link">Open Debug Panel</a>
    <script>function copy(id){ const link = "{{ url }}/Mostak?id=" + id; navigator.clipboard.writeText(link); alert('Copied!'); }</script>
    </body></html>
    """
    return render_template_string(html, channels=CHANNELS, url=request.host_url.rstrip('/'))

@app.route('/debug')
def debug():
    return f"""
    <body style="background:#000; color:#0f0; font-family:monospace; padding:20px;">
    <h2>Mostak Proxy Debug System</h2>
    <hr>
    <p>Last Session Refresh: {debug_info['last_refresh']}</p>
    <p>Current Status: {debug_info['status']}</p>
    <p>Using Fallback Cookie: {debug_info['using_fallback']}</p>
    <hr>
    <p>Active Cookies in Session:</p>
    <pre>{debug_info['cookies_found']}</pre>
    <hr>
    <button onclick="location.reload()">Refresh Debug Info</button>
    <a href="/" style="color:#fff; margin-left:20px;">Back to Home</a>
    </body>
    """

@app.route('/Mostak')
def stream():
    id = request.args.get('id')
    if not id: return home()
    target = f"https://bldcmprod-cdn.toffeelive.com/cdn/live/{id}" if ("slang" in id or ".m3u8" in id) else f"https://bldcmprod-cdn.toffeelive.com/cdn/live/{id}/playlist.m3u8"
    return proxy(target)

@app.route('/proxy')
def proxy_call():
    url = request.args.get('url')
    return proxy(url)

def proxy(url):
    try:
        headers = BASE_HEADERS.copy()
        if debug_info["using_fallback"] or 'Edge-Cache-Cookie' not in client.cookies:
            headers['Cookie'] = FALLBACK_COOKIE
        
        r = client.get(url, headers=headers, timeout=15)
        if r.status_code == 403: # Retry once with refresh
            refresh_session()
            r = client.get(url, headers=headers, timeout=15)

        if ".m3u8" in url:
            lines = r.text.split('\n')
            new = []
            base = url.rsplit('/', 1)[0] + "/"
            for line in lines:
                line = line.strip()
                if not line: continue
                if "#EXT-X-KEY" in line:
                    u = line.split('URI="')[1].split('"')[0]
                    line = line.replace(u, f"{request.host_url.rstrip('/')}/proxy?url={urljoin(base, u)}")
                elif not line.startswith('#'):
                    line = f"{request.host_url.rstrip('/')}/proxy?url={urljoin(base, line)}"
                new.append(line)
            return Response('\n'.join(new), mimetype='application/vnd.apple.mpegurl')
        return Response(r.content, mimetype=r.headers.get('Content-Type'))
    except: return "Error", 500

if __name__ == '__main__':
    refresh_session()
    app.run(host='0.0.0.0', port=8080)
