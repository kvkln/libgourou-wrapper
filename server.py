import asyncio
from fastapi import FastAPI, HTTPException, Request, status, UploadFile
from fastapi.staticfiles import StaticFiles
import os.path

app = FastAPI()


app.mount("/", StaticFiles(directory="/app/www", html=True), name="static")

