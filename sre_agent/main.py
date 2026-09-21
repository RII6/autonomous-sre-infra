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
active_alerts = {} # Хранит текущие активные алерты: { "AlertName": {details} }
BLOCKED_THREATS = Counter('sre_blocked_threats_total', 'Total blocked threats')

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

class ThreatPayload(BaseModel):
    ip: str
    username: str
    password: str

@app.get("/api/agent/state")
def get_state():
    return {
        "threats_blocked_count": threats_blocked_count,
        "active_alerts": list(active_alerts.values())
    }

@app.post("/api/webhook/threat")
def handle_threat(payload: ThreatPayload):
    global threats_blocked_count
    print(f"[HONEYPOT] Атака от {payload.ip} с кредами {payload.username}:{payload.password}")
    
    if payload.ip == "127.0.0.1" or payload.ip.endswith(".1"):
        print(f"[WHITELIST] IP {payload.ip} является шлюзом или localhost. Блокировка в Nginx пропущена.")
    else:
        try:
            with open("/project/nginx/blocklist.conf", "a") as f:
                f.write(f"deny {payload.ip};\n")
            print(f"[DEFENSE] IP {payload.ip} добавлен в черный список Nginx!")
            subprocess.run(["docker-compose", "-p", "autonomous-sre-infra", "exec", "-T", "nginx", "nginx", "-s", "reload"], cwd="/project")
        except Exception as e:
            print(f"[ERROR] Ошибка блокировки: {e}")

    threats_blocked_count += 1
    BLOCKED_THREATS.inc()
    return {"status": "banned", "ip": payload.ip}

@app.post("/api/webhook/alert")
def handle_alert(payload: dict):
    try:
        alerts = payload.get("alerts", [])
        for alert in alerts:
            alertname = alert.get("labels", {}).get("alertname", "")
            status = alert.get("status")
            summary = alert.get("annotations", {}).get("summary", alertname)
            severity = alert.get("labels", {}).get("severity", "info")
            
            if status == "firing":
                active_alerts[alertname] = {
                    "name": alertname,
                    "summary": summary,
                    "severity": severity
                }
            elif status == "resolved" and alertname in active_alerts:
                del active_alerts[alertname]
                
            if status == "firing":
                if alertname == "HighLatency_DDoS":
                    print(f"[ALERTMANAGER] Алерт HighLatency_DDoS!")
                    print(f"[SELF-HEALING] Запускаю экстренное масштабирование: app=2")
                    cmd = ["docker-compose", "-p", "autonomous-sre-infra", "up", "--scale", "app=2", "-d", "app"]
                    subprocess.run(cmd, cwd="/project")
                    # Перезагружаем Nginx для обновления статического upstream (чтобы keepalive подхватил новые IP)
                    subprocess.run(["docker-compose", "-p", "autonomous-sre-infra", "exec", "-T", "nginx", "nginx", "-s", "reload"], cwd="/project")
                    
                elif alertname == "BackendDead":
                    print(f"[ALERTMANAGER] Алерт BackendDead!")
                    print(f"[SELF-HEALING] Воскрешаю упавший сервис...")
                    cmd = ["docker-compose", "-p", "autonomous-sre-infra", "up", "--scale", "app=1", "-d", "app"]
                    subprocess.run(cmd, cwd="/project")
                    subprocess.run(["docker-compose", "-p", "autonomous-sre-infra", "exec", "-T", "nginx", "nginx", "-s", "reload"], cwd="/project")

                elif alertname == "LowLoad_ScaleDown":
                    print(f"[ALERTMANAGER] Алерт LowLoad_ScaleDown!")
                    print(f"[AUTO-SCALING] Нагрузка спала. Уменьшаю количество реплик до: app=1")
                    cmd = ["docker-compose", "-p", "autonomous-sre-infra", "up", "--scale", "app=1", "-d", "app"]
                    subprocess.run(cmd, cwd="/project")
                    subprocess.run(["docker-compose", "-p", "autonomous-sre-infra", "exec", "-T", "nginx", "nginx", "-s", "reload"], cwd="/project")
                
        return {"status": "success", "message": "Alerts processed"}
    except Exception as e:
        print(f"[ERROR] Ошибка обработки алерта: {e}")
        return {"status": "error"}

@app.post("/api/agent/attack/ssh")
def trigger_ssh_attack():
    print("[ATTACK] Запуск реальной утилиты Hydra для брутфорса Ханипота...")
    # Проверяем наличие образа local/hydra. Если нет - собираем его и "запекаем" зависимости.
    # После этого запускаем атаку мгновенно из кэшированного образа.
    cmd = "docker image inspect local/hydra >/dev/null 2>&1 || printf 'FROM alpine\\nRUN apk add --no-cache hydra\\nENTRYPOINT [\"hydra\"]\\n' | docker build -t local/hydra - ; docker run --rm --network sre_defense_net local/hydra -l root -p 123456 ssh://honeypot:2222"
    subprocess.Popen(cmd, shell=True) # Асинхронно, чтобы не блокировать API
    return {"status": "success", "message": "Hydra attack launched"}

@app.post("/api/agent/attack/load")
def trigger_load_attack():
    print("[ATTACK] Запуск генератора нагрузки hey на эндпоинт /api/heavy...")
    # Шлем 60 секунд нагрузки напрямую на бэкенды.
    # Ограничиваем QPS до ~700 RPS (50 потоков * 14 qps), чтобы 1 сервер задыхался, а 2 сервера справлялись идеально.
    cmd = "docker run --rm --network sre_defense_net williamyeh/hey -z 120s -c 250 -q 14 http://nginx:80/api/internal_heavy"
    subprocess.Popen(cmd, shell=True)
    return {"status": "success", "message": "Load test launched"}

@app.post("/api/agent/attack/kill")
def trigger_kill_container():
    print("[ATTACK] Жесткое убиство контейнера app...")
    cmd = "docker rm -f autonomous-sre-infra-app-1"
    subprocess.Popen(cmd, shell=True)
    return {"status": "success", "message": "Backend killed"}
