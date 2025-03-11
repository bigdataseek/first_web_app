FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Gunicorn 실행
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"] 
