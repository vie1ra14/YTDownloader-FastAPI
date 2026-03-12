# type: ignore
import tempfile
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .dependencies import validate_url, remove_file
import yt_dlp

app = FastAPI()

app.mount("/", StaticFiles(directory="static", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yt-downloader-fast-api.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


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
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
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
