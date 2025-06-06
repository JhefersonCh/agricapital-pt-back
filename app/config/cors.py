from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()


def setup_cors(app: FastAPI):
    origins = []
    if os.getenv("ENVIRONMENT") == "development":
        origins.append("*")
    else:
        origins.append(os.getenv("FRONTEND_URL").rstrip("/"))
    methods = os.getenv("ALLOWED_METHODS", "GET,POST,PATCH,DELETE,OPTIONS").split(",")
    headers = os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization").split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=methods,
        allow_headers=headers,
    )
