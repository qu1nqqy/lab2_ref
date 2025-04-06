from fastapi.security import HTTPBasicCredentials
from utils import templates
from starlette.requests import Request
from db import UserTable, TaskTable, session_deps

from services.calendar_service import MyCalendar
from datetime import datetime, timedelta

from core.auth import basic_auth


def admin(request: Request, credentials: HTTPBasicCredentials):
    username = basic_auth(credentials)

    today = datetime.now()
    next_w = today + timedelta(days=7)

    user =  session_deps.query(UserTable).filter(UserTable.username == username).first()
    tasks = session_deps.query(TaskTable).filter(TaskTable.user_id == user.id).all() if user else []
    session_deps.close()

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
