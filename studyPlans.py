from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
import os
import re
import logging
from subject_utils import extract_subject_name

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

def save_to_chromadb(text, metadata, chroma_path="./chromadb_store"):
    lines = text.splitlines()
    
    discipline_names = [extract_subject_name(line) for line in lines if line.strip()]
    text4search = "\n".join(discipline_names)
    
    metadata['text_with_hours'] = text
    embeddings = HuggingFaceEmbeddings(model_name="deepvk/USER-bge-m3")
    db = Chroma(embedding_function=embeddings, persist_directory=chroma_path)
    db.add_texts([text4search], metadatas=[metadata])
    
# Загрузка плана в .pdf

def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    full_text = []

    for i, page in enumerate(documents):
        if (i > 0) and (i < 7):
          text = page.page_content
          full_text.append(text)

    return " ".join(full_text)

# Обработка учебного плана

def clean_subject(subject):
    if "КСР" in subject:
        subject = subject.split("КСР", 1)[1]
        subject = re.sub(r"^[\d\s]+", "", subject)
    tokens = subject.split()
    valid_start = None
    for i, token in enumerate(tokens):
        token_stripped = token.strip(" .,-")
        if re.match(r'^(?:[A-ZА-ЯЁ]|[0-9]+[A-ZА-ЯЁ])', token_stripped):
            valid_start = i
            break
    if valid_start is None:
        return ""
    tokens = tokens[valid_start:]
    return " ".join(tokens).strip()
    
def extract_subjects(raw_text):
    pattern = r"^([A-Za-zА-Яа-яЁё0-9\s\(\)\-,.]+?)\s*Б1\.(?:[ОВ]\.\d+(?:\.\d+)*|\d+(?:\.\d+)*?)\s+(\d+(?:,\s*\d+)*)\b(?:\s+(\d+))?"

    matches = re.findall(pattern, raw_text, flags=re.MULTILINE)
    if not matches:
        logger.warning("Нет совпадений")
        return 0

    subjects = []
    for subject, token1, token2 in matches:
        subject_clean = " ".join(subject.split())
        subject_clean = clean_subject(subject_clean)
        if re.search(r"\(А\)$", subject_clean):
            continue
        token1_clean = token1.replace(" ", "")
        if ("," in token1_clean) or (token1_clean.isdigit() and int(token1_clean) < 10):
            hours = token2 if token2 else token1_clean
        else:
            hours = token1_clean
        if (subject_clean != ""):
            subject_clean = re.sub(r'\s+', ' ', subject_clean).strip()
            subjects.append(f"{subject_clean} - {hours} часов")
    return "\n".join(subjects)

# Загрузка файлов и запуск функции

def save_study_plans():
    logger.info("Программа начала работу")

    pdf_dir = "StudyPlans"

    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            raw_text = process_pdf(pdf_path)
            cleaned = extract_subjects(raw_text)
            logger.info(f"Файл: {filename} обрабатывается")
            save_to_chromadb(cleaned, {"filename": filename})
            logger.info(f"Файл: {filename} сохранен")
