from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import math
import time

app = FastAPI(title="Target Web Server (App)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем сборщик реальных метрик RED (Rate, Errors, Duration)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.get("/api/heavy")
def compute_heavy():
    """
    Эндпоинт для генерации реальной нагрузки на процессор.
    При Load-тестировании вызовы этого метода тысячами запросов в секунду 
    нагрузят процессор до 100% и увеличат Latency в Grafana.
    """
    # Симуляция тяжелых вычислений
    result = 0
    for i in range(1, 10000):
        result += math.sqrt(i)
    return {"status": "success"}

@app.get("/api/health")
def healthcheck():
    return {"status": "ok"}