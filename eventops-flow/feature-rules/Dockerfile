FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py local_sink.py ./
CMD ["sh","-lc","python -u app.py & python -u local_sink.py"]
