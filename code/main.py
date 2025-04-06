from fastapi import FastAPI

from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from utils import templates
app = FastAPI(
    title='TODO App using FastAPI',
    description='A simple TODO app',
    version='0.9 beta'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse(
        request,
        'index.html',
        {
            'request': request
        }
    )


from routers import admin_router, auth_router, task_router

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(task_router)
