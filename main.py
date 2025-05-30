from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.requests.controllers.request_controller import requestRouter
from app.modules.clients.controllers.client_controller import clientRouter
from app.modules.notifications.controllers.notification_controller import (
    notificationRouter,
)
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AgriCapital API",
    description="Backend para la prueba técnica de AgriCapital",
    version="1.0.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return "Bienvenido a la API de AgriCapital"


app.include_router(requestRouter)
app.include_router(clientRouter)
app.include_router(notificationRouter)
