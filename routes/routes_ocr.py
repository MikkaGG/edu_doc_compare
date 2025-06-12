import os
import logging
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from choosePlan import get_best_study_plan
from differenceHours import get_difference_hours

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.post("/upload_pdf/", tags=["Загрузка файлов"], response_class=HTMLResponse)
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    try:
        temp_path = f"temp_{file.filename}"
        # Сохраняем загруженный файл во временное хранилище
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Вызываем функцию обработки из choosePlan.py
        best_plan_filename, extracted_text, best_plan_extracted = get_best_study_plan(temp_path, file.filename)
    
        comparsion_output = get_difference_hours(best_plan_extracted, extracted_text)
        
        response_text = f"Наиболее подходящий план обучения: {best_plan_filename}\n" + comparsion_output
        os.remove(temp_path)
        
        return templates.TemplateResponse("uploadFile.html", {"request": request, "result": response_text, "filename": file.filename})
    except Exception as e:
        return {"error": str(e)}
