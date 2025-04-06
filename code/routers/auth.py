from fastapi import APIRouter
from services import user_service
from starlette.requests import Request
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["auth"])

@router.get('/register')
def read_register(request: Request):
    return user_service.read_register(request)


@router.post('/register')
async def create_register(request: Request):
    return await user_service.create_register(request)


@router.get('/logout')
def logout(request: Request):
    return RedirectResponse('/', status_code=401)