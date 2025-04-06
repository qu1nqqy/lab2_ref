from starlette.requests import Request
from utils import templates, pattern, pattern_pw, pattern_mail
from db import UserTable, session_deps


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


async def create_register(request: Request):
    data = await request.form()
    username = data.get('username')
    password = data.get('password')
    password_tmp = data.get('password_tmp')
    mail = data.get('mail')

    error = []

    tmp_user = session_deps.query(UserTable).filter(UserTable.username == username).first()

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
    session_deps.add(user)
    session_deps.commit()
    session_deps.close()

    return templates.TemplateResponse(
        request,
        'complete.html',
        {
            'request': request,
            'username': username
        }
    )
