# type: ignore
import tempfile
import os
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .dependencies import validate_url, remove_file
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yt-downloader-fast-api.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


@app.get('/download')
async def download(background_task: BackgroundTasks,
                   url: str = Depends(validate_url)):
    title = ''
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    path = temp.name
    finalpath = path + '.mp3'
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": path + ".%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,

        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },

        "extractor_args": {
            "youtube": {
                "player_client": ["android"],
                "player_skip": ["webpage", "configs"],
            }
        },

        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ytdl:
        info = ytdl.extract_info(url)
        title = info.get('title')
        ytdl.download([url])

    background_task.add_task(remove_file, finalpath)

    return FileResponse(
        finalpath,
        media_type="audio/mpeg",
        filename=f"{title}.mp3",
    )

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
