FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y tesseract-ocr \
					tesseract-ocr-rus \
					poppler-utils && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install  python-multipart \
				--no-cache-dir -r requirements.txt

ADD routes routes
ADD templates templates
COPY main.py studyPlans.py choosePlan.py differenceHours.py subject_utils.py .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "on"]

