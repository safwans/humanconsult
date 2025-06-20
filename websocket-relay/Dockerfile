FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY relay_server.py .
RUN pip install hypercorn
CMD ["hypercorn", "relay_server:app", "--bind", "0.0.0.0:8080", "--worker-class", "uvloop"]
