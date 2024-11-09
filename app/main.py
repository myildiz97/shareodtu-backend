from fastapi import FastAPI

from config.routers_config import routers
from config.config import connect_to_database


app = FastAPI(
    title="ShareODTÜ API",
    on_startup=[connect_to_database],
)


# Include all routers
for router in routers:
    app.include_router(router=router)
