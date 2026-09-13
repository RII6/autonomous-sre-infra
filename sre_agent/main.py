from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(title="SRE Control Plane Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Метрики для UI и Prometheus
threats_blocked_count = 0
BLOCKED_THREATS = Counter('sre_blocked_threats_total', 'Total blocked threats')

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

class ThreatPayload(BaseModel):
    ip: str
    username: str
    password: str

@app.get("/api/agent/state")
def get_state():
    return {"threats_blocked_count": threats_blocked_count}

@app.post("/api/webhook/threat")
def handle_threat(payload: ThreatPayload):
    global threats_blocked_count
    print(f"[HONEYPOT] Атака от {payload.ip} с кредами {payload.username}:{payload.password}")
    threats_blocked_count += 1
    BLOCKED_THREATS.inc()
    return {"status": "banned", "ip": payload.ip}

@app.post("/api/webhook/alert")
def handle_alert(payload: dict):
    try:
        alerts = payload.get("alerts", [])
        for alert in alerts:
            alertname = alert.get("labels", {}).get("alertname", "")
            
            if alertname == "HighLatency_DDoS":
                print(f"[ALERTMANAGER] Алерт HighLatency_DDoS!")
                print(f"[SELF-HEALING] Запускаю экстренное масштабирование: app=2")
                cmd = ["docker-compose", "-p", "autonomous-sre-infra", "up", "--scale", "app=2", "-d", "app"]
                subprocess.run(cmd, cwd="/project")
                
            elif alertname == "BackendDead":
                print(f"[ALERTMANAGER] Алерт BackendDead!")
                print(f"[SELF-HEALING] Воскрешаю упавший сервис...")
                cmd = ["docker-compose", "-p", "autonomous-sre-infra", "up", "--scale", "app=1", "-d", "app"]
                subprocess.run(cmd, cwd="/project")
                
        return {"status": "success", "message": "Alerts processed"}
    except Exception as e:
        print(f"[ERROR] Ошибка обработки алерта: {e}")
        return {"status": "error"}

@app.post("/api/agent/attack/ssh")
def trigger_ssh_attack():
    print("[ATTACK] Запуск реальной утилиты Hydra для брутфорса Ханипота...")
    # Запускаем контейнер в той же сети, который брутфорсит honeypot
    cmd = "docker run --rm --network sre_defense_net alpine sh -c 'apk add --no-cache hydra && hydra -l root -p 123456 ssh://honeypot:2222'"
    subprocess.Popen(cmd, shell=True) # Асинхронно, чтобы не блокировать API
    return {"status": "success", "message": "Hydra attack launched"}

@app.post("/api/agent/attack/load")
def trigger_load_attack():
    print("[ATTACK] Запуск генератора нагрузки hey на эндпоинт /api/heavy...")
    # Шлем 30 секунд нагрузки напрямую на бэкенды в обход rate-limit Nginx
    cmd = "docker run --rm --network sre_defense_net williamyeh/hey -z 30s -c 50 http://app:8000/api/heavy"
    subprocess.Popen(cmd, shell=True)
    return {"status": "success", "message": "Load test launched"}

@app.post("/api/agent/attack/kill")
def trigger_kill_container():
    print("[ATTACK] Жесткое убиство контейнера app...")
    cmd = "docker rm -f autonomous-sre-infra-app-1"
    subprocess.Popen(cmd, shell=True)
    return {"status": "success", "message": "Backend killed"}
