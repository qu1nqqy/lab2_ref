from fastapi import APIRouter
from services import task_service
from fastapi import Depends, Form
from fastapi.security import HTTPBasicCredentials
from starlette.requests import Request
from deps import security

router = APIRouter(tags=["tasks"])


@router.get('/todo/{username}/{year}/{month}/{day}')
def read_detail(request: Request, username, year, month, day, credentials: HTTPBasicCredentials = Depends(security)):
    return task_service.read_detail(request, username, year, month, day, credentials)


@router.post('/done')
async def done(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    return await task_service.done(request, credentials)


@router.post('/add')
async def add_task(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    return await task_service.add_task(request, credentials)


@router.get('/delete/{task_id}')
def delete_task(request: Request, task_id, credentials: HTTPBasicCredentials = Depends(security)):
    return task_service.delete_task(request, task_id, credentials)


@router.get('/get')
def get(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    return task_service.get(request, credentials)


@router.post('/add_task')
async def insert_task(
        request: Request,
        content: str = Form(...),
        deadline: str = Form(...),
        credentials: HTTPBasicCredentials = Depends(security)
):
    return await task_service.insert_task(request, content, deadline, credentials)
