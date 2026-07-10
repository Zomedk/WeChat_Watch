from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.models.database import engine
from app.models.schemas import Base
from app.api.routes import router as api_router
from app.api.login import router as login_router
from app.scheduler.tasks import start_scheduler, shutdown_scheduler
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="微信公众号文章监控系统")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(api_router, prefix="/api")
app.include_router(login_router, prefix="/auth")

@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "app/static/index.html"))

@app.on_event("startup")
def startup():
    start_scheduler()

@app.on_event("shutdown")
def shutdown():
    shutdown_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
