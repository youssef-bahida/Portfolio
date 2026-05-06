#  docker run -p 5000:5000 -v "$env:USERPROFILE\Desktop:/downloads" -e DOWNLOAD_DIR=/downloads yt-downloader
#1. Clique sur Images dans le menu gauche, trouve yt-downloader, clique Run
#2. Une fenêtre s'ouvre — clique sur Optional settings pour dérouler les options
#3. Configure comme ça :

#Ports → 5000 : 5000
#Volumes → Host path : C:\Users\parco\Desktop | Container path : /downloads
#Environment variables → DOWNLOAD_DIR = /downloads

#4. Clique Run
#
#
import os
import re
import json
import queue
import threading
import pathlib
import platform
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import yt_dlp

app = Flask(__name__)

# --- Per-session download queues ---
download_queues: dict[str, queue.Queue] = {}
download_status: dict[str, dict] = {}

def get_desktop_path() -> pathlib.Path:
    # Check if a custom path is set via environment variable
    custom = os.environ.get("DOWNLOAD_DIR")
    if custom:
        return pathlib.Path(custom)
    
    system = platform.system()
    if system == "Windows":
        return pathlib.Path(os.path.join(os.path.expanduser("~"), "Desktop"))
    elif system == "Darwin":
        return pathlib.Path(os.path.expanduser("~/Desktop"))
    else:
        xdg = os.environ.get("XDG_DESKTOP_DIR")
        if xdg:
            return pathlib.Path(xdg)
        return pathlib.Path(os.path.expanduser("~/Desktop"))

def sanitize_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def make_progress_hook(session_id: str, q: queue.Queue):
    def hook(d):
        if d["status"] == "downloading":
            q.put({
                "type": "progress",
                "filename": os.path.basename(d.get("filename", "")),
                "percent": d.get("_percent_str", "0%").strip(),
                "speed": d.get("_speed_str", "N/A").strip(),
                "eta": d.get("_eta_str", "N/A").strip(),
                "downloaded": d.get("downloaded_bytes", 0),
                "total": d.get("total_bytes") or d.get("total_bytes_estimate", 0),
            })
        elif d["status"] == "finished":
            q.put({
                "type": "finished_file",
                "filename": os.path.basename(d.get("filename", "")),
            })
        elif d["status"] == "error":
            q.put({
                "type": "error_file",
                "filename": os.path.basename(d.get("filename", "unknown")),
            })
    return hook

def run_download(session_id: str, url: str, q: queue.Queue):
    desktop = get_desktop_path()

    # First, extract playlist info to get name
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            playlist_title = sanitize_name(info.get("title") or info.get("id") or "playlist")
            total_videos = len(info.get("entries") or [])
    except Exception as e:
        q.put({"type": "fatal", "message": str(e)})
        return

    folder_name = f"playlist_{playlist_title}"
    output_dir = desktop / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    q.put({
        "type": "start",
        "playlist_title": playlist_title,
        "total": total_videos,
        "output_dir": str(output_dir),
    })

    opts = {
    "format": "bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    "merge_output_format": "mp4",
    "outtmpl": str(output_dir / "%(playlist_index)s - %(title)s.%(ext)s"),
    "ignoreerrors": True,
    "yesplaylist": True,
    "retries": 5,
    "fragment_retries": 5,
    "progress_hooks": [make_progress_hook(session_id, q)],
    "download_archive": str(output_dir / ".archive.txt"),
    "quiet": True,
    "no_warnings": True,
    # ❌ supprime complètement le bloc postprocessors
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        q.put({"type": "done", "output_dir": str(output_dir)})
    except Exception as e:
        q.put({"type": "fatal", "message": str(e)})

# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.json
    url = (data or {}).get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    session_id = os.urandom(8).hex()
    q = queue.Queue()
    download_queues[session_id] = q
    download_status[session_id] = {"running": True}

    thread = threading.Thread(target=run_download, args=(session_id, url, q), daemon=True)
    thread.start()

    return jsonify({"session_id": session_id})

@app.route("/api/stream/<session_id>")
def stream(session_id):
    q = download_queues.get(session_id)
    if not q:
        return jsonify({"error": "Invalid session"}), 404

    def generate():
        while True:
            try:
                msg = q.get(timeout=30)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg["type"] in ("done", "fatal"):
                    break
            except queue.Empty:
                yield "data: {\"type\": \"ping\"}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

if __name__ == "__main__":
    print("\n🎬  YT Downloader running at http://localhost:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
