import requests
import time
from flask import Flask, Response, request, render_template_string
from urllib.parse import urljoin

app = Flask(__name__)
client = requests.Session()

debug_info = {
    "last_refresh": "Never",
    "status": "Initializing",
    "using_fallback": True,
    "cookies_found": {}
}

# Jekhetu Auto-Cookie kaj korche na (Vercel IP Blocked), ei Cookie tai ashol. Expire hole eita change korben.
FALLBACK_COOKIE = "Edge-Cache-Cookie=URLPrefix=aHR0cHM6Ly9ibGRjbXByb2QtY2RuLnRvZmZlZWxpdmUuY29t:Expires=1771927793:KeyName=prod_linear:Signature=mmxHt_ttcVgH3693d9c5EIGfVhH34xSHljuGSIipfM1970qE_szW-a3ZRVDNhF9SywWpzUEZ4z1wDUhAOX2sAg"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://toffeelive.com/",
    "Origin": "https://toffeelive.com",
}

# Ekebare Clean IDs mapped with exact paths
CHANNEL_MAP = {
    "somoy_tv": "slang/somoy_tv_320/somoy_tv_320.m3u8?bitrate=768000",
    "jamuna_tv": "slang/jamuna_tv_576/jamuna_tv_576.m3u8?bitrate=1000000",
    "independent_tv": "slang/independent_tv_576/independent_tv_576.m3u8?bitrate=1000000",
    "movie_bangla": "slang/movie_bangla_576/movie_bangla_576.m3u8?bitrate=1000000",
    "anandatv": "anandatv/playlist.m3u8",
    "sony_sports_1": "sony_sports_1_hd/playlist.m3u8",
    "sony_sports_2": "sony_sports_2_hd/playlist.m3u8",
    "sony_sports_5": "sony_sports_5_hd/playlist.m3u8",
    "ten_cricket": "ten_cricket/playlist.m3u8",
    "sonybbc_earth": "sonybbc_earth_hd/playlist.m3u8",
    "sonyyay": "sonyyay/playlist.m3u8",
    "sonyaath": "sonyaath/playlist.m3u8",
    "and_tv": "and_tv_hd/playlist.m3u8",
    "ekhon_tv": "ekhon_tv/playlist.m3u8",
    "ekattor_tv": "ekattor_tv/playlist.m3u8",
    "nexus_tv": "nexus_tv/playlist.m3u8",
    "mohona_tv": "mohona_tv/playlist.m3u8",
    "desh_tv": "desh_tv/playlist.m3u8",
    "global_tv": "global_tv/playlist.m3u8",
    "asian_tv": "asian_tv/playlist.m3u8",
    "toffee_movie": "toffee_movie/playlist.m3u8"
}

def refresh_session():
    try:
        client.get("https://toffeelive.com/", headers=BASE_HEADERS, timeout=10)
        debug_info["last_refresh"] = time.strftime('%Y-%m-%d %H:%M:%S')
        ck = client.cookies.get_dict()
        debug_info["cookies_found"] = ck
        if 'Edge-Cache-Cookie' in ck:
            debug_info["status"] = "Auto Cookie Success"
            debug_info["using_fallback"] = False
        else:
            debug_info["status"] = "Fallback Active (Toffee Blocked Vercel IP for Auto Cookie)"
            debug_info["using_fallback"] = True
    except Exception as e:
        debug_info["status"] = f"Handshake Failed: {str(e)}"
        debug_info["using_fallback"] = True

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mostak Proxy</title>
        <style>
            body { font-family: sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; display: flex; justify-content: center; }
            .container { max-width: 650px; width: 100%; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
            h1 { color: #38bdf8; text-align: center; font-size: 28px; margin-bottom: 5px; }
            .usage { background: #0f172a; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #38bdf8; font-family: monospace; font-size: 13px; word-break: break-all; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .card { background: #334155; padding: 12px; border-radius: 8px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; border: 1px solid transparent; transition: 0.2s; }
            .card:hover { border-color: #38bdf8; background: #1e293b; }
            .ch-name { font-size: 14px; font-weight: bold; }
            .ch-id { font-size: 10px; color: #94a3b8; }
            .debug-link { display: block; text-align: center; margin-top: 25px; color: #94a3b8; text-decoration: none; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>MOSTAK PROXY</h1>
            <p style="text-align:center; color:#94a3b8; font-size:14px;">High Quality Toffee Live Streaming</p>
            <div class="usage">Endpoint Example:<br> <span style="color:#38bdf8;">{{ host }}/Mostak?id=somoy_tv</span></div>
            <div class="grid">
                {% for key, val in channels.items() %}
                <div class="card" onclick="copy('{{ key }}')">
                    <div>
                        <div class="ch-name">{{ key | replace('_', ' ') | title }}</div>
                        <div class="ch-id">id: {{ key }}</div>
                    </div>
                    <span style="font-size: 11px; color: #38bdf8; font-weight: bold;">COPY</span>
                </div>
                {% endfor %}
            </div>
            <a href="/debug" class="debug-link">Check Debug Panel</a>
        </div>
        <script>
            function copy(id) {
                const url = "{{ host }}/Mostak?id=" + id;
                navigator.clipboard.writeText(url);
                alert('Stream link copied!\\nURL: ' + url);
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, channels=CHANNEL_MAP, host=request.host_url.rstrip('/'))

@app.route('/debug')
def debug():
    return f"""
    <body style="background:#000; color:#00ff00; font-family:monospace; padding:30px; line-height:1.6;">
        <h2>Mostak System Debugger</h2>
        <hr border="1" color="#333">
        <p>Refresh Time : {debug_info['last_refresh']}</p>
        <p>Current Status: {debug_info['status']}</p>
        <p>Using Fallback: {debug_info['using_fallback']}</p>
        <hr border="1" color="#333">
        <p>Session Cookies (What Toffee gave us):</p>
        <pre style="background:#111; padding:15px; overflow-x: auto; color:#fff;">{debug_info['cookies_found']}</pre>
        <p style="color:#ff4444;">* Note: If 'Edge-Cache-Cookie' is not in the list above, Toffee blocked Vercel IP. You MUST update the fallback cookie manually.</p>
        <br>
        <button onclick="location.reload()" style="padding:10px 20px; cursor:pointer; background:#333; color:#0f0; border:none;">RE-CHECK</button>
        <a href="/" style="color:#fff; margin-left:20px; text-decoration:none;">BACK HOME</a>
    </body>
    """

@app.route('/Mostak')
def stream_handler():
    chid = request.args.get('id')
    if not chid: return home()
    
    # Check if user typed a mapped ID (e.g. 'somoy_tv')
    if chid in CHANNEL_MAP:
        url = f"https://bldcmprod-cdn.toffeelive.com/cdn/live/{CHANNEL_MAP[chid]}"
    else:
        # Fallback for dynamic/unknown channels (e.g. 'anandatv')
        url = f"https://bldcmprod-cdn.toffeelive.com/cdn/live/{chid}/playlist.m3u8"
        
    return execute_proxy(url)

@app.route('/proxy')
def proxy_handler():
    url = request.args.get('url')
    if not url: return "No URL", 400
    return execute_proxy(url)

def execute_proxy(url):
    try:
        headers = BASE_HEADERS.copy()
        # Vercel IP khaoay auto kaj korbe na, tai Fallback oboshshoi dite hobe
        headers['Cookie'] = FALLBACK_COOKIE
        
        r = client.get(url, headers=headers, timeout=15)
        
        if ".m3u8" in url:
            lines = r.text.split('\n')
            refined = []
            base = url.rsplit('/', 1)[0] + "/"
            for line in lines:
                line = line.strip()
                if not line: continue
                if "#EXT-X-KEY" in line:
                    u = line.split('URI="')[1].split('"')[0]
                    line = line.replace(u, f"{request.host_url.rstrip('/')}/proxy?url={urljoin(base, u)}")
                elif not line.startswith('#'):
                    line = f"{request.host_url.rstrip('/')}/proxy?url={urljoin(base, line)}"
                refined.append(line)
            return Response('\n'.join(refined), mimetype='application/vnd.apple.mpegurl')
        return Response(r.content, mimetype=r.headers.get('Content-Type'))
    except Exception as e:
        return f"Stream Error: {str(e)}", 500

refresh_session()

if __name__ == '__main__':
    app.run()
