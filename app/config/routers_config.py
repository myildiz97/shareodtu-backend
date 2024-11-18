# User Routes
from routers.users.users_base import router as UserRouters
from routers.auth.auth_base import router as AuthRouters
from routers.foods.foods_base import router as FoodRouters

routers = [
    UserRouters,
    AuthRouters,
    FoodRouters,
]
