FROM python:3.12-slim
WORKDIR /app
COPY enricher/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY enricher/main.py ./main.py
COPY ../common /app/common
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
