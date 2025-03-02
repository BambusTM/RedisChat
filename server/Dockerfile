FROM python:3.10

WORKDIR /app

COPY server.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
