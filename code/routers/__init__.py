from .admin import router as admin_router
from .auth import router as auth_router
from .tasks import router as task_router

__all__ = [
    "admin_router",
    "auth_router",
    "task_router"
]
