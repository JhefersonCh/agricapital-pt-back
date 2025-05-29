from fastapi import FastAPI
from app.modules.requests.controllers.request_controller import requestRouter

app = FastAPI(
    title="AgriCapital API",
    description="Backend para la prueba técnica de AgriCapital",
    version="1.0.0",
)


@app.get("/")
def index():
    return "Bienvenido a la API de AgriCapital"


app.include_router(requestRouter)
