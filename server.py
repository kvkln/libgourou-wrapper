import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import os.path
import uuid


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.isdir('/app/.adept'):
        proc = await asyncio.create_subprocess_exec(
            'adept_activate', '--anonymous', '--random-serial', '--output-dir', '/tmp/.adept')
        await proc.communicate()
        if proc.returncode != 0:
            raise Exception('adobe activation failed')
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/convert")
async def convert_files(file: Annotated[bytes, File()]):

    async def exe(*args):
        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,  stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=stdout.decode() + stderr.decode())

    uid = uuid.uuid4().hex
    tmpdirname = f'/tmp/{uid}'
    os.makedirs(tmpdirname)
    input_filepath = f'{tmpdirname}/book.acsm'
    with open(input_filepath, 'wb') as f:
        f.write(file)
    await exe('acsmdownloader', '--adept-directory', '/tmp/.adept', '--output-dir', tmpdirname, input_filepath)
    try:
        filename = os.path.basename(next((entry for entry in os.listdir(tmpdirname) if entry != 'book.acsm')))
    except StopIteration:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='No file downloaded')
    await exe(
        'adept_remove', '--adept-directory', '/tmp/.adept', '--output-dir', tmpdirname,
        '--output-file', 'out.epub', os.path.join(tmpdirname, filename)
    )
    return FileResponse(f'{tmpdirname}/out.epub', filename=filename)


app.mount("/", StaticFiles(directory="/app/www", html=True), name="static")
