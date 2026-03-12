# type: ignore
import os
from fastapi import HTTPException
from urllib.parse import urlparse


ALLOWED_SCHEMES = {"http", "https"}
LINK_LIST = {"www.youtube.com", "youtu.be", "youtube.com"}


def validate_url(url: str):
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise HTTPException(status_code=400, detail="Invalid URL scheme")

    if parsed.netloc not in LINK_LIST:
        raise HTTPException(status_code=400, detail="Invalid link")

    return url


def remove_file(path):
    if os.path.exists(path):
        os.remove(path)
