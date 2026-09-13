import asyncio
import urllib.request
import urllib.parse
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [HONEYPOT] - %(message)s')

# Адрес нашего бэкенда во внутренней сети Docker
BACKEND_WEBHOOK_URL = "http://sre_agent:8001/api/webhook/threat"

async def handle_client(reader, writer):
    # Получаем IP адрес того, кто подключился
    addr = writer.get_extra_info('peername')
    attacker_ip = addr[0]
    
    logging.info(f"🚨 ОБНАРУЖЕНО ПОДКЛЮЧЕНИЕ 🚨 IP: {attacker_ip}")

    # Отправляем фейковое приветствие SSH, чтобы бот подумал, что это настоящий сервер
    fake_banner = b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n"
    writer.write(fake_banner)
    await writer.drain()

    # Ждем, пока хакер пришлет логин и пароль (читаем до 1024 байт), но не парсим их
    try:
        data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
        logging.info(f"Получены зашифрованные данные от {attacker_ip} (размер: {len(data)} байт).")
    except asyncio.TimeoutError:
        logging.info(f"Таймаут от {attacker_ip}.")

    # Закрываем соединение
    logging.info(f"Закрываем соединение с {attacker_ip}. Отправляем репорт на бэкенд...")
    writer.close()
    await writer.wait_closed()

    # Отправляем webhook на бэкенд
    try:
        payload = json.dumps({"ip": attacker_ip, "type": "SSH Brute-force / Port Scan", "username": "unknown", "password": "unknown"}).encode('utf-8')
        req = urllib.request.Request(BACKEND_WEBHOOK_URL, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            logging.info(f"Бэкенд ответил: {response.getcode()}")
    except Exception as e:
        logging.error(f"Не удалось отправить webhook на бэкенд: {e}")

async def main():
    # Запускаем сервер на порту 2222
    server = await asyncio.start_server(handle_client, '0.0.0.0', 2222)
    
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    logging.info(f"Ловушка (Honeypot) активирована! Слушаем порт 2222 на {addrs}")

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
