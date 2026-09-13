import socket
import time

print("💀 Запуск скрипта-хакера (Симуляция атаки)")
print("Сканирование портов целевой системы (localhost)...")

TARGET_HOST = '127.0.0.1'
TARGET_PORT = 2222

try:
    print(f"\n[+] Обнаружен открытый порт {TARGET_PORT}. Попытка подключения (SSH)...")
    
    # Подключаемся к ханипоту
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3.0)
    s.connect((TARGET_HOST, TARGET_PORT))
    
    # Читаем приветствие сервера
    banner = s.recv(1024).decode('utf-8').strip()
    print(f"[+] Сервер ответил: {banner}")
    
    print("[-] Запуск брутфорса (перебор паролей)...")
    # Пытаемся отправить логин и пароль
    s.send(b"root\n")
    time.sleep(0.5)
    s.send(b"123456\n")
    
    print("[!] Соединение неожиданно разорвано сервером. Похоже, нас обнаружили!")
    s.close()
except ConnectionRefusedError:
    print(f"[X] Ошибка: Не удалось подключиться к порту {TARGET_PORT}. Ханипот выключен?")
except Exception as e:
    print(f"[X] Неизвестная ошибка: {e}")
