from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from routes import routes_ocr
from studyPlans import save_study_plans
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import shutil

# Добавить статусы кода

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app : FastAPI):
    save_study_plans()
    yield
    store_path = "chromadb_store"
    if os.path.exists(store_path):
        shutil.rmtree(store_path)
        print("База данных успешно очищена.")
        
app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Подключаем роутер с эндпоинтами для OCR
app.include_router(routes_ocr.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
