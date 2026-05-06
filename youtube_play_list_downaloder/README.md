# 🎬 YT Playlist Downloader

> Download entire YouTube playlists as high-quality **MP4 files** (H.264 + AAC) — directly to your Desktop. No codec installs, no hassle.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red?style=flat-square)

---

## ✨ What it does

- 📋 Paste a YouTube playlist URL → everything downloads automatically
- 🎞️ Merges video + audio into a single `.mp4` per video (no silent files)
- 📁 Creates a named folder on your Desktop (`playlist_[name]/`)
- 📡 Real-time progress tracking in the browser — speed, ETA, per-video status
- ♻️ Skips already-downloaded videos (download archive)
- 🐳 Fully containerized — runs anywhere Docker runs

---

## 🚀 Quick Start with Docker

### 1 — Pull the image

```bash
bahida2026youssef/yt-downloader
```

> Or build it yourself from source — see [Build from source](#-build-from-source) below.

---

### 2 — Run the container

Pick the command for your OS:

**🪟 Windows (CMD)**
```cmd
docker run -p 5000:5000 -v "%USERPROFILE%\Desktop:/downloads" -e DOWNLOAD_DIR=/downloads yt-downloader
```

**🪟 Windows (PowerShell)**
```powershell
docker run -p 5000:5000 -v "$env:USERPROFILE\Desktop:/downloads" -e DOWNLOAD_DIR=/downloads yt-downloader
```

**🐧 Linux / 🍎 macOS**
```bash
docker run -p 5000:5000 -v ~/Desktop:/downloads -e DOWNLOAD_DIR=/downloads yt-downloader
```

---

### 3 — Open the app

Go to **[http://localhost:5000](http://localhost:5000)** in your browser.

---

### 4 — Download a playlist

1. Open YouTube and navigate to the playlist you want
2. Copy the URL from your **browser address bar**
3. Paste it into the input field and click **▶ Download**
4. Watch the real-time progress — files land on your Desktop when done 🎉

---

## ⚙️ Configuration

| Variable | Description | Default |
|---|---|---|
| `DOWNLOAD_DIR` | Where files are saved inside the container | `~/Desktop` |
| `PORT` | Port the web server listens on | `5000` |

> The `-v` flag maps a folder on your real machine into the container. Without it, downloaded files stay trapped inside the container and won't appear on your Desktop.

---

## 🐳 Docker Desktop (GUI)

Prefer a graphical interface? Use Docker Desktop:

1. Go to **Images** → find `yt-downloader` → click **Run**
2. Click **Optional settings**
3. Fill in:
   - **Ports** → `5000` : `5000`
   - **Volumes** → Host path: `C:\Users\YourName\Desktop` | Container path: `/downloads`
   - **Environment variables** → `DOWNLOAD_DIR` = `/downloads`
4. Click **Run** then open **http://localhost:5000**

---

## 🛠️ Build from Source

```bash
# Clone the repo
git clone https://github.com/youssef-bahida/Portfolio.git
cd Portfolio/youtube_play_list_downaloder

# Build the image (FFmpeg is installed automatically)
docker build -t yt-downloader .

# Run it
docker run -p 5000:5000 -v ~/Desktop:/downloads -e DOWNLOAD_DIR=/downloads yt-downloader


docker pull bahida2026youssef/yt-downloader
```

> FFmpeg is baked into the Docker image — no manual installation needed.

---

## 📁 Project Structure

```
yt-downloader/
├── app.py              # Flask backend + yt-dlp download logic
├── Dockerfile          # Docker build (Python 3.12 + FFmpeg)
├── requirements.txt    # Python dependencies
└── templates/
    └── index.html      # Web UI (real-time progress)
```

---

## 🔧 Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12, Flask |
| Downloader | yt-dlp |
| Media processing | FFmpeg (H.264 + AAC) |
| Frontend | Vanilla JS, Server-Sent Events |
| Container | Docker |

---

## ⚠️ Notes

- Playlist must be **public or unlisted** — private playlists cannot be downloaded
- Downloads use H.264 + AAC for maximum compatibility (plays on Windows, Mac, phones, TVs)
- Already-downloaded videos are skipped automatically on re-run

---

## 📄 License

MIT — do whatever you want with it.
