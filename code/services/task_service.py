from fastapi.security import HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from utils import templates
from starlette.requests import Request
from db import UserTable, TaskTable, session_deps

from datetime import datetime

from core.auth import basic_auth


def read_detail(request: Request, username, year, month, day, credentials: HTTPBasicCredentials):
    username_tmp = basic_auth(credentials)
    if username_tmp != username:
        return RedirectResponse('/')

    user = session_deps.query(UserTable).filter(UserTable.username == username).first()
    user_all_tasks = session_deps.query(TaskTable).filter(TaskTable.user_id == user.id).all()
    session_deps.close()

    theday = f'{year}{month.zfill(2)}{day.zfill(2)}'
    tasks = [t for t in user_all_tasks if t.deadline.strftime('%Y%m%d') == theday]

    return templates.TemplateResponse(
        request,
        'detail.html',
        {
            'request': request,
            'username': username,
            'tasks': tasks,
            'year': year,
            'month': month,
            'day': day
        }
    )


async def done(request: Request, credentials: HTTPBasicCredentials):
    username = basic_auth(credentials)
    user = session_deps.query(UserTable).filter(UserTable.username == username).first()
    user_all_tasks = session_deps.query(TaskTable).filter(TaskTable.user_id == user.id).all()

    data = await request.form()
    t_dones = data.getlist('done[]')

    for task in user_all_tasks:
        if str(task.id) in t_dones:
            task.done = True

    session_deps.commit()
    session_deps.close()

    return RedirectResponse('/admin')


async def add_task(request: Request, credentials: HTTPBasicCredentials):
    username = basic_auth(credentials)
    user = session_deps.query(UserTable).filter(UserTable.username == username).first()

    data = await request.form()
    year = int(data['year'])
    month = int(data['month'])
    day = int(data['day'])
    hour = int(data['hour'])
    minute = int(data['minute'])

    deadline = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    task = TaskTable(user.id, data['content'], deadline)

    session_deps.add(task)
    session_deps.commit()
    session_deps.close()

    return RedirectResponse('/admin')


def delete_task(request: Request, task_id, credentials: HTTPBasicCredentials):
    username = basic_auth(credentials)
    user = session_deps.query(UserTable).filter(UserTable.username == username).first()
    task = session_deps.query(TaskTable).filter(TaskTable.id == task_id).first()

    if task.user_id != user.id:
        return RedirectResponse('/admin')

    session_deps.delete(task)
    session_deps.commit()
    session_deps.close()

    return RedirectResponse('/admin')


def get(request: Request, credentials: HTTPBasicCredentials):
    username = basic_auth(credentials)
    user = session_deps.query(UserTable).filter(UserTable.username == username).first()
    tasks = session_deps.query(TaskTable).filter(TaskTable.user_id == user.id).all()
    session_deps.close()

    return [{
        'id': task.id,
        'content': task.content,
        'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'publishd': task.date.strftime('%Y-%m-%d %H:%M:%S'),
        'done': task.done,
    } for task in tasks]


async def insert_task(
        request: Request,
        content: str,
        deadline: str,
        credentials: HTTPBasicCredentials
):
    username = basic_auth(credentials)
    user = session_deps.query(UserTable).filter(UserTable.username == username).first()

    task = TaskTable(user.id, content, datetime.strptime(deadline, '%Y-%m-%d_%H:%M:%S'))
    session_deps.add(task)
    session_deps.commit()

    new_task = session_deps.query(TaskTable).all()[-1]
    session_deps.close()

    return {
        'id': new_task.id,
        'content': new_task.content,
        'deadline': new_task.deadline.strftime('%Y-%m-%d_%H:%M:%S'),
        'published': new_task.date.strftime('%Y-%m-%d_%H:%M:%S'),
        'done': new_task.done,
    }
