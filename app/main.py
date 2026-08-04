from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(title="SRE Defense API")

# Разрешаем запросы от фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "system": "Infrastructure Immune System", "health": "stable"}

@app.get("/api/metrics")
def get_mock_metrics():
    # Имитируем метрики для дашборда
    return {
        "cpu_usage": random.randint(15, 45),
        "memory_usage": random.randint(40, 65),
        "active_connections": random.randint(120, 350),
        "threats_blocked": random.randint(3, 12)
    }

@app.post("/api/simulate/attack")
def simulate_attack(attack_type: str):
    return {
        "status": "success",
        "message": f"Simulation of '{attack_type}' initiated successfully.",
        "action_taken": "Triggered defense protocol, monitoring metrics."
    }