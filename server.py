import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import shutil
import time
import traceback
from fastapi import FastAPI, HTTPException, status, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import os.path
import uuid

cleanup_dirs = set()


async def cleanup_tempdirs():
    while True:
        try:
            for d in cleanup_dirs:
                if time.time() - os.stat(d).st_mtime > 10:
                    shutil.rmtree(d)
                    cleanup_dirs.remove(d)
        except Exception:
            traceback.print_exc()
        finally:
            await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.isdir('/app/.adept'):
        proc = await asyncio.create_subprocess_exec('adept_activate', '--anonymous', '--random-serial', '--output-dir', '/tmp/.adept')
        await proc.communicate()
        if proc.returncode != 0:
            raise Exception('adobe activation failed')
    asyncio.create_task(cleanup_tempdirs())
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/convert")
async def convert_files(file: Annotated[bytes, File()]):

    async def exe(*args):
        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,  stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=stdout.decode() + stderr.decode())

    tmpdirname = f'/tmp/{uuid.uuid4().hex}'
    os.makedirs(tmpdirname)
    input_filepath = f'{tmpdirname}/book.acsm'
    with open(input_filepath, 'wb') as f:
        f.write(file)
    await exe('acsmdownloader', '--adept-directory', '/tmp/.adept', '--output-dir', tmpdirname, input_filepath)
    try:
        filename = os.path.basename(next((entry for entry in os.listdir(tmpdirname) if entry != 'book.acsm')))
    except StopIteration:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='No file downloaded')
    tmp_filename = 'out' + Path(filename).suffix
    await exe(
        'adept_remove', '--adept-directory', '/tmp/.adept', '--output-dir', tmpdirname,
        '--output-file', tmp_filename, os.path.join(tmpdirname, filename)
    )
    cleanup_dirs.add(tmpdirname)
    return FileResponse(os.path.join(tmpdirname, tmp_filename), filename=filename)


app.mount("/", StaticFiles(directory="/app/www", html=True), name="static")
