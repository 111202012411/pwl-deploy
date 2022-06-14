#!/usr/bin/env python

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from typing import Callable

from .routes import router

app = FastAPI()

@app.middleware("http")
async def middleware(request: Request, call_next: Callable) -> Response:

    response: Response
    response = await call_next(request)
    response.headers.update({
        # "Server": "Apache/2.4.53 (Ubuntu) OpenSSL/1.1.1o",
        "Server": "Apache/2.4.53 (Ubuntu)",
        "X-Powered-By": "PHP/8.1.6"
    })

    return response

app.include_router(router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
