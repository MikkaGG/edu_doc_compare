import os
import re
import logging
from pdf2image import convert_from_path
import pytesseract
from subject_utils import extract_subject_name

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

def should_filter_token(token):
    preposition_list = ['с', 'и', 'на', 'из', 'в', 'для', 'по', 'к', 'баз']
    if re.fullmatch(r'\d+', token):
        return True
    if len(token) in [1, 2, 3]:
        if re.search(r'\d[A-Z]|[A-Z]\d', token):
            return False
        if token in preposition_list:
            return False
        return True
    return False

def extract(text):
    pattern = r"^\d+\.\s*((?:(?:[A-Za-zА-ЯЁа-яё,.\":()\-])|\d(?!\d))+(?:\s+(?:(?:[A-Za-zА-ЯЁа-яё,.\":()\-])|\d(?!\d))+)*)(?:\s*\*\*)?\s+.*?(\d+)(?:[.,])?\s*час"
    matches = re.findall(pattern, text, re.MULTILINE)
    subjects = []
    for subject, hours in matches:
        subject_clean = re.sub(r'[^\w\s()-]', '', subject)
        tokens = subject_clean.split()
        tokens = [token for token in tokens if not should_filter_token(token)]
        cleaned_subject = " ".join(tokens)
        subjects.append(f"{cleaned_subject} - {hours} часов")
    return "\n".join(subjects)

def perform_ocr(pdf_path):
    pages = convert_from_path(pdf_path, dpi=800)
    extracted_text = ""
    for page in pages:
        text = pytesseract.image_to_string(page, lang='rus+eng')
        extracted_text += text + "\n"
    return extracted_text

# Функция для поиска лучшего учебного плана (используем ранее описанные функции)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def find_text(text, chroma_path="./chromadb_store"):
    embeddings = HuggingFaceEmbeddings(model_name="deepvk/USER-bge-m3")
    db = Chroma(embedding_function=embeddings, persist_directory=chroma_path)
    results = db.similarity_search(text, k=1)
    return results[0] if results else None

def get_best_study_plan(pdf_path, file_name):
    logger.info(f"Файл {file_name} принят на обработку")
    # Выполняем OCR
    extracted_text = perform_ocr(pdf_path)
    logger.info(f"Файл {file_name} обработан OCR")
    # Обрабатываем полученный текст
    cleaned = extract(extracted_text)
    discipline_names4search = "\n".join([extract_subject_name(line) for line in cleaned.splitlines() if line.strip()])
    # Ищем лучший учебный план
    studyPlan = find_text(discipline_names4search)
    if studyPlan:
        best_plan_filename = studyPlan.metadata.get('filename')
        logger.info(f"Наиболее подходящий план обучения: {best_plan_filename}")
        return best_plan_filename, cleaned, studyPlan
    else:
        logger.warning("Не удалось найти подходящий план обучения")
        return None, cleaned
