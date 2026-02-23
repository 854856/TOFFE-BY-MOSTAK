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

# UPDATE THIS WHEN IT EXPIRES
FALLBACK_COOKIE = "Edge-Cache-Cookie=URLPrefix=aHR0cHM6Ly9ibGRjbXByb2QtY2RuLnRvZmZlZWxpdmUuY29t:Expires=1771927793:KeyName=prod_linear:Signature=mmxHt_ttcVgH3693d9c5EIGfVhH34xSHljuGSIipfM1970qE_szW-a3ZRVDNhF9SywWpzUEZ4z1wDUhAOX2sAg"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://toffeelive.com/",
    "Origin": "https://toffeelive.com",
}

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
            debug_info["status"] = "Fallback Active (Datacenter IP Blocked)"
            debug_info["using_fallback"] = True
    except Exception as e:
        debug_info["status"] = f"Handshake Failed"
        debug_info["using_fallback"] = True

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mostak API Documentation</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <style>
            :root { --bg: #000000; --text: #ededed; --border: #333333; --accent: #0070f3; --code-bg: #111111; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; line-height: 1.6; }
            .navbar { border-bottom: 1px solid var(--border); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; background: rgba(0,0,0,0.8); backdrop-filter: blur(10px); }
            .navbar h1 { margin: 0; font-size: 18px; font-weight: 600; letter-spacing: -0.5px; }
            .navbar a { color: #888; text-decoration: none; font-size: 14px; transition: color 0.2s; }
            .navbar a:hover { color: #fff; }
            .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
            h2 { font-size: 24px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-top: 40px; font-weight: 500; }
            p { color: #a1a1aa; font-size: 15px; }
            .code-block { background: var(--code-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; font-family: 'Fira Code', monospace; font-size: 13px; color: #34d399; overflow-x: auto; margin: 15px 0; display: flex; justify-content: space-between; align-items: center; }
            .copy-btn { background: #222; border: 1px solid #444; color: #fff; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; transition: 0.2s; }
            .copy-btn:hover { background: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border); }
            th { color: #fff; font-weight: 500; }
            td { color: #a1a1aa; }
            td code { background: #222; padding: 2px 6px; border-radius: 4px; color: #f472b6; font-family: 'Fira Code', monospace; font-size: 12px; }
            .toast { position: fixed; bottom: 20px; right: 20px; background: var(--accent); color: #fff; padding: 10px 20px; border-radius: 6px; font-size: 14px; display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <h1>Mostak API Docs</h1>
            <a href="/debug" target="_blank">Debug System &rarr;</a>
        </nav>
        
        <div class="container">
            <p>Welcome to the Mostak Proxy documentation. Use these endpoints to stream live Bangladeshi TV channels bypassing CORS and authentication locks.</p>

            <h2>1. Base Endpoint</h2>
            <p>To access any live stream, use the following endpoint structure. Pass the channel ID as a query parameter.</p>
            <div class="code-block">
                <span id="base-url">GET {{ host }}/Mostak?id={channel_id}</span>
            </div>

            <h2>2. Available Channels</h2>
            <p>Here is the list of supported channels and their corresponding IDs. Click the copy button to grab the full streaming URL.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Channel Name</th>
                        <th>Parameter ID</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for key, val in channels.items() %}
                    <tr>
                        <td>{{ key | replace('_', ' ') | title }}</td>
                        <td><code>{{ key }}</code></td>
                        <td><button class="copy-btn" onclick="copyUrl('{{ key }}')">Copy URL</button></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div id="toast" class="toast">URL Copied to clipboard!</div>

        <script>
            function copyUrl(id) {
                const url = "{{ host }}/Mostak?id=" + id;
                navigator.clipboard.writeText(url);
                const toast = document.getElementById('toast');
                toast.style.display = 'block';
                setTimeout(() => toast.style.display = 'none', 2500);
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, channels=CHANNEL_MAP, host=request.host_url.rstrip('/'))

@app.route('/debug')
def debug():
    return f"""
    <body style="background:#0a0a0a; color:#10b981; font-family:'Fira Code', monospace; padding:40px; line-height:1.6; font-size:14px;">
        <h2 style="color:#fff;">System Diagnostics</h2>
        <div style="border: 1px solid #333; padding: 20px; border-radius: 6px; background: #111;">
            <p><strong>Last Ping:</strong> {debug_info['last_refresh']}</p>
            <p><strong>Auth Status:</strong> {debug_info['status']}</p>
            <p><strong>Fallback Mode:</strong> {debug_info['using_fallback']}</p>
        </div>
        <h3 style="color:#fff; margin-top:30px;">Extracted Session Data</h3>
        <pre style="background:#000; border: 1px solid #333; padding:15px; border-radius:6px; color:#a1a1aa; overflow-x: auto;">{debug_info['cookies_found']}</pre>
        <div style="margin-top: 20px;">
            <button onclick="location.reload()" style="background:#fff; color:#000; border:none; padding:8px 16px; border-radius:4px; cursor:pointer; font-weight:bold;">Run Test Again</button>
            <a href="/" style="color:#888; margin-left:15px; text-decoration:none;">&larr; Back to Docs</a>
        </div>
    </body>
    """

@app.route('/Mostak')
def stream_handler():
    chid = request.args.get('id')
    if not chid: return home()
    if chid in CHANNEL_MAP:
        url = f"https://bldcmprod-cdn.toffeelive.com/cdn/live/{CHANNEL_MAP[chid]}"
    else:
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
