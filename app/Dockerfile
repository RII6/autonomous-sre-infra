FROM python:3.11-slim
RUN apt-get update && apt-get install -y docker.io docker-compose-plugin || apt-get install -y docker.io docker-compose
RUN useradd -m appusr
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=root:root ./main.py ./
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000