from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from config.routers_config import routers
from config.config import connect_to_database


app = FastAPI(
    title="ShareODTÜ API",
    on_startup=[connect_to_database],
)

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "https://shareodtu.vercel.app/",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex="https://.*\.vercel.app",
)


# Include all routers
for router in routers:
    app.include_router(router=router)
