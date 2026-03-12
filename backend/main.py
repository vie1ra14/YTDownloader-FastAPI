# type: ignore
import tempfile
import shutil
import os
from fastapi import FastAPI, Depends, HTTPException
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
SECRET_COOKIE_PATH = "/etc/secrets/cookies.txt"
COOKIE_PATH = "/tmp/cookies.txt"
CLIENTS = [
    "android",
    "android_music",
    "ios",
    "tv_embedded",
    "web",
]

if os.path.exists(SECRET_COOKIE_PATH) and not os.path.exists(COOKIE_PATH):
    shutil.copy(SECRET_COOKIE_PATH, COOKIE_PATH)


@app.get('/download')
async def download(background_task: BackgroundTasks,
                   url: str = Depends(validate_url)):
    title = ''
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    path = temp.name
    finalpath = path + '.mp3'
    for client in CLIENTS:
        try:
            ydl_opts = {
                "format": "bestaudio[ext=m4a]/bestaudio/best",
                "outtmpl": path + ".%(ext)s",
                "cookiefile": "/tmp/cookies.txt",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,

                "retries": 3,
                "fragment_retries": 3,
                "sleep_interval": 1,
                "max_sleep_interval": 3,

                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    )
                },

                "extractor_args": {
                    "youtube": {
                        "player_client": [client]
                    }
                },

                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ytdl:
                info = ytdl.extract_info(url, download=True)
                title = info.get('title')

            background_task.add_task(remove_file, finalpath)

            return FileResponse(
                finalpath,
                media_type="audio/mpeg",
                filename=f"{title}.mp3",
            )

        except Exception as e:
            print(f'Client {client} failed:', e)
    raise HTTPException(status_code=500, detail='All Youtube clients failed.')


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
