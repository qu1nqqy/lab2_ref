from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from services import admin_service
from starlette.requests import Request
from deps import security

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post('')
def admin(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    return admin_service.admin(request, credentials)
