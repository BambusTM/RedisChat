FROM python:3.10

WORKDIR /app

COPY client.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "client.py"]
