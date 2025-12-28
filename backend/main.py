from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.machines import router as machines_api_router
from api.v1.network_data_source import router as network_data_source_api_router
from api.v1.tags import router as tags_router
from api.v1.related_tags import router as related_tags_router
from api.v1.script import router as script_router
from api.v1.report import router as report

# from core.config import settings


app = FastAPI(title="ToolStatix")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(machines_api_router)
app.include_router(network_data_source_api_router)
app.include_router(tags_router)
app.include_router(related_tags_router)
app.include_router(report)


# Testing script
app.include_router(script_router)


# Delete later
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI - ToolStatix!"}