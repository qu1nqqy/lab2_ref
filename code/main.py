from fastapi import FastAPI, Depends, HTTPException, Form, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse

from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.middleware.cors import CORSMiddleware

from typing import List
import hashlib  # used for passwords
import re       # for regular expressions

import db
from models import UserTable, TaskTable

from mycalendar import MyCalendar
from datetime import datetime, timedelta

from auth import basic_auth

security = HTTPBasic()

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

templates = Jinja2Templates(directory='templates')

# Regex for username: 4–20 alphanumeric characters
pattern = re.compile(r'\w{4,20}')
# Regex for password: 6–20 alphanumeric characters
pattern_pw = re.compile(r'\w{6,20}')
# Regex for email
pattern_mail = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse(
        request,
        'index.html',
        {
            'request': request
        }
    )


@app.get('/admin')
@app.post('/admin')
def admin(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    username = basic_auth(credentials)

    today = datetime.now()
    next_w = today + timedelta(days=7)

    user = db.session.query(UserTable).filter(UserTable.username == username).first()
    tasks = db.session.query(TaskTable).filter(TaskTable.user_id == user.id).all() if user else []
    db.session.close()

    cal = MyCalendar(
        username,
        {
            t.deadline.strftime('%Y%m%d'): t.done for t in tasks
        }
    ).formatyear(today.year, 4)

    tasks = [task for task in tasks if today <= task.deadline]
    links = [t.deadline.strftime(f'/todo/{username}/%Y/%m/%d') for t in tasks]

    return templates.TemplateResponse(
        request,
        'admin.html',
        {
            'request': request,
            'user': user,
            'tasks': tasks,
            'links': links,
            'calendar': cal
        }
    )


@app.get('/register')
def read_register(request: Request):
    return templates.TemplateResponse(
        request,
        'register.html',
        {
            'request': request,
            'username': '',
            'error': []
        }
    )


@app.post('/register')
async def create_register(request: Request):
    data = await request.form()
    username = data.get('username')
    password = data.get('password')
    password_tmp = data.get('password_tmp')
    mail = data.get('mail')

    error = []

    tmp_user = db.session.query(UserTable).filter(UserTable.username == username).first()

    if tmp_user is not None:
        error.append('Username already exists')
    if password != password_tmp:
        error.append('Passwords do not match')
    if pattern.match(username) is None:
        error.append('Username must be 4-20 alphanumeric characters')
    if pattern_pw.match(password) is None:
        error.append('Password must be 6-20 alphanumeric characters')
    if pattern_mail.match(mail) is None:
        error.append('Invalid email address')

    if error:
        return templates.TemplateResponse(
            request,
            'register.html',
            {
                'request': request,
                'username': username,
                'error': error
            }
        )

    user = UserTable(username, password, mail)
    db.session.add(user)
    db.session.commit()
    db.session.close()

    return templates.TemplateResponse(
        request,
        'complete.html',
        {
            'request': request,
            'username': username
        }
    )


@app.get('/todo/{username}/{year}/{month}/{day}')
def read_detail(request: Request, username, year, month, day, credentials: HTTPBasicCredentials = Depends(security)):
    username_tmp = basic_auth(credentials)
    if username_tmp != username:
        return RedirectResponse('/')

    user = db.session.query(UserTable).filter(UserTable.username == username).first()
    user_all_tasks = db.session.query(TaskTable).filter(TaskTable.user_id == user.id).all()
    db.session.close()

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


@app.post('/done')
async def done(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    username = basic_auth(credentials)
    user = db.session.query(UserTable).filter(UserTable.username == username).first()
    user_all_tasks = db.session.query(TaskTable).filter(TaskTable.user_id == user.id).all()

    data = await request.form()
    t_dones = data.getlist('done[]')

    for task in user_all_tasks:
        if str(task.id) in t_dones:
            task.done = True

    db.session.commit()
    db.session.close()

    return RedirectResponse('/admin')


@app.post('/add')
async def add_task(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    username = basic_auth(credentials)
    user = db.session.query(UserTable).filter(UserTable.username == username).first()

    data = await request.form()
    year = int(data['year'])
    month = int(data['month'])
    day = int(data['day'])
    hour = int(data['hour'])
    minute = int(data['minute'])

    deadline = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    task = TaskTable(user.id, data['content'], deadline)

    db.session.add(task)
    db.session.commit()
    db.session.close()

    return RedirectResponse('/admin')


@app.get('/delete/{task_id}')
def delete_task(request: Request, task_id, credentials: HTTPBasicCredentials = Depends(security)):
    username = basic_auth(credentials)
    user = db.session.query(UserTable).filter(UserTable.username == username).first()
    task = db.session.query(TaskTable).filter(TaskTable.id == task_id).first()

    if task.user_id != user.id:
        return RedirectResponse('/admin')

    db.session.delete(task)
    db.session.commit()
    db.session.close()

    return RedirectResponse('/admin')


@app.get('/get')
def get(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    username = basic_auth(credentials)
    user = db.session.query(UserTable).filter(UserTable.username == username).first()
    tasks = db.session.query(TaskTable).filter(TaskTable.user_id == user.id).all()
    db.session.close()

    return [{
        'id': task.id,
        'content': task.content,
        'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'publishd': task.date.strftime('%Y-%m-%d %H:%M:%S'),
        'done': task.done,
    } for task in tasks]


@app.post('/add_task')
async def insert_task(
    request: Request,
    content: str = Form(...),
    deadline: str = Form(...),
    credentials: HTTPBasicCredentials = Depends(security)
):
    username = basic_auth(credentials)
    user = db.session.query(UserTable).filter(UserTable.username == username).first()

    task = TaskTable(user.id, content, datetime.strptime(deadline, '%Y-%m-%d_%H:%M:%S'))
    db.session.add(task)
    db.session.commit()

    new_task = db.session.query(TaskTable).all()[-1]
    db.session.close()

    return {
        'id': new_task.id,
        'content': new_task.content,
        'deadline': new_task.deadline.strftime('%Y-%m-%d_%H:%M:%S'),
        'published': new_task.date.strftime('%Y-%m-%d_%H:%M:%S'),
        'done': new_task.done,
    }


@app.get('/logout')
def logout(request: Request):
    return RedirectResponse('/', status_code=401)
