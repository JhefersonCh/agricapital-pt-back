from fastapi import FastAPI
from app.config.cors import setup_cors
from app.config.security import SecurityHeadersMiddleware
from app.modules.requests.controllers.request_controller import requestRouter
from app.modules.clients.controllers.client_controller import clientRouter
from app.modules.notifications.controllers.notification_controller import (
    notificationRouter,
)
from app.ws.controllers.websocket_routes import router as websocketRouter
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AgriCapital API",
    description="Backend para la prueba técnica de AgriCapital",
    version="1.0.0",
)

setup_cors(app)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/")
def index():
    return "Bienvenido a la API de AgriCapital"


app.include_router(requestRouter)
app.include_router(clientRouter)
app.include_router(notificationRouter)
app.include_router(websocketRouter)
