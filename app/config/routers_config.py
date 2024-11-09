# User Routes
from routers.users.users_base import router as UserRouters
from routers.auth.auth_base import router as AuthRouters

routers = [
    UserRouters,
    AuthRouters,
]
