import json
import os
import socket
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRESENTER_PIN = os.getenv("PRESENTER_PIN", "2468")

QUESTIONS = [
    {
        "round":"Ronda 1 · Cadena alimentaria",
        "q":"¿Cuál es el orden correcto de la cadena presentada?",
        "o":[
            "Venta → Producción → Selección → Procesamiento",
            "Producción → Selección → Procesamiento → Venta",
            "Selección → Venta → Producción → Procesamiento",
            "Procesamiento → Producción → Venta → Selección"
        ],
        "a":1,
        "exp":"Producción → Selección → Procesamiento → Venta.",
        "icons":["🏭","🌾","🚚","🛒"]
    },
    {
        "round":"Ronda 1 · Cadena alimentaria",
        "q":"¿Qué sector se encarga de los procesos de la cadena alimenticia de la sociedad?",
        "o":["Industria textil","Industria alimentaria","Industria automotriz","Industria minera"],
        "a":1,
        "exp":"La industria alimentaria.",
        "icons":["🏭","🌾","🚚","🛒"]
    },
    {
        "round":"Ronda 2 · Química",
        "q":"¿Cuál de estos es un proceso químico mencionado en la presentación?",
        "o":["Fermentación","Colorante","Saborizante","Conservante"],
        "a":0,
        "exp":"Fermentación. También aparecen pasteurización, hidrogenación y emulsificación.",
        "icons":["🧪","🥛","🍞","🧫"]
    },
    {
        "round":"Ronda 2 · Química",
        "q":"¿Cuál de estos aparece como sustancia química usada en alimentos?",
        "o":["Pasteurización","Hidrogenación","Antioxidantes","Fermentación"],
        "a":2,
        "exp":"Antioxidantes. También se mencionan saborizantes, colorantes, fortificantes, acidulantes y conservantes.",
        "icons":["🧪","🥛","🍞","🧫"]
    },
    {
        "round":"Ronda 3 · Empresas",
        "q":"¿Qué empresa se presenta como la empresa de alimentos más grande del mundo?",
        "o":["Alpina","Grupo Nutresa","Nestlé","PepsiCo"],
        "a":2,
        "exp":"Nestlé.",
        "icons":["☕","🍫","🍪","🥤"]
    },
    {
        "round":"Ronda 3 · Empresas",
        "q":"¿Qué empresa colombiana se describe como productora de alimentos a base de lácteos y derivados?",
        "o":["Alpina","PepsiCo","Nestlé","Grupo Nutresa"],
        "a":0,
        "exp":"Alpina.",
        "icons":["🥛","🍦","🧃","🍓"]
    },
    {
        "round":"Ronda 3 · Empresas",
        "q":"¿Qué empresa colombiana fabrica y vende galletas, chocolates, café, embutidos, helados y pastas?",
        "o":["PepsiCo","Grupo Nutresa","Alpina","Nestlé"],
        "a":1,
        "exp":"Grupo Nutresa.",
        "icons":["🍪","🍫","☕","🍝"]
    },
    {
        "round":"Ronda 4 · Salud pública",
        "q":"Según la presentación, ¿qué característica favorece el aumento de ultraprocesados?",
        "o":["Son difíciles de consumir","Duran poco tiempo","Son fáciles de consumir y duran mucho","No tienen sabor"],
        "a":2,
        "exp":"Son fáciles de consumir, duran mucho tiempo y pueden sustituir alimentos menos procesados.",
        "icons":["🍔","🍟","🍭","❤️"]
    },
    {
        "round":"Ronda 4 · Controversias",
        "q":"¿Cuál NO aparece entre las controversias listadas?",
        "o":["Aumento de azúcares","Daño ambiental","Desinformación digital","Turismo internacional"],
        "a":3,
        "exp":"Turismo internacional no aparece. Sí aparecen aumento de azúcares, daño ambiental, ENT y desinformación digital.",
        "icons":["🍬","🌍","📱","❤️"]
    },
    {
        "round":"Ronda 5 · Impacto económico",
        "q":"¿Qué afirma la presentación sobre el empleo?",
        "o":["La industria elimina casi todos los empleos","Solo genera empleo en tiendas","Sostiene millones de empleos directos e indirectos","No tiene impacto laboral"],
        "a":2,
        "exp":"Sostiene millones de empleos directos e indirectos, desde productores hasta distribuidores y consumidores finales.",
        "icons":["💼","💸","🏢","🌍"]
    },
    {
        "round":"Ronda 5 · Impacto económico",
        "q":"¿Cómo describe la presentación el peso económico de la industria?",
        "o":["Como un sector pequeño","Como un gigante financiero y social","Como una actividad exclusivamente local","Como un sector sin impacto global"],
        "a":1,
        "exp":"Como un gigante financiero y social a escala global.",
        "icons":["💼","💸","🏢","🌍"]
    },
    {
        "round":"Ronda 6 · Futuro",
        "q":"¿Cuál es una tendencia futura mencionada?",
        "o":["Eliminar la tecnología","Reducir toda la producción","Usar inteligencia artificial y laboratorios","Abandonar la sostenibilidad"],
        "a":2,
        "exp":"La presentación plantea una industria tecnológica, sostenible y personalizada, impulsada por laboratorios e inteligencia artificial.",
        "icons":["🤖","🌱","🔬","🍽️"]
    },
    {
        "round":"Ronda 6 · Futuro",
        "q":"¿Qué reto futuro se menciona?",
        "o":["Producir menos alimentos","Aumentar la producción para una población creciente","Eliminar los productos orgánicos","Dejar de innovar"],
        "a":1,
        "exp":"Aumentar la producción para abastecer a una población en constante crecimiento.",
        "icons":["🤖","🌱","🔬","🍽️"]
    },
    {
        "round":"Ronda final · Conclusión",
        "q":"La industria alimentaria, según la conclusión, es...",
        "o":["Solo un sistema para fabricar comida","Un pilar socioeconómico y financiero que enfrenta retos de salud, sostenibilidad e innovación","Una actividad sin impacto social","Un sector que no cambia con el tiempo"],
        "a":1,
        "exp":"Es un pilar socioeconómico y financiero global que impulsa economía y empleo y evoluciona ante retos de salud pública y sostenibilidad.",
        "icons":["🌍","🏭","❤️","🚀"]
    },
]

LOCK = threading.Lock()
STATE = {
    "question_index": 0,
    "revealed": False,
    "scores": [0,0,0,0],
    "leaders": [None,None,None,None],
    "submissions": [None,None,None,None],
    "response_times": [None,None,None,None],
    "awarded_points": [0,0,0,0],
    "awarded": False,
    "start_time": None,
    "deadline": None,
    "base_url": "",
}

def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"
    finally:
        s.close()

def public_state(base_url=None):
    with LOCK:
        idx = STATE["question_index"]
        phase = "questions" if idx < len(QUESTIONS) else "final"
        q = QUESTIONS[idx] if phase == "questions" else None
        effective_base = (base_url or STATE.get("base_url") or "").rstrip("/")
        out = {
            "phase": phase,
            "question_index": idx,
            "question_count": len(QUESTIONS),
            "revealed": STATE["revealed"],
            "scores": list(STATE["scores"]),
            "leaders": list(STATE["leaders"]),
            "submissions": list(STATE["submissions"]),
            "response_times": list(STATE["response_times"]),
            "awarded_points": list(STATE["awarded_points"]),
            "start_time": STATE["start_time"],
            "deadline": STATE["deadline"],
            "base_url": effective_base,
            "join_links":[f'{effective_base}/lider?equipo={i+1}' for i in range(4)]
        }
        if q:
            out["question"] = {
                "round": q["round"],
                "q": q["q"],
                "o": q["o"],
                "icons": q["icons"],
            }
            if STATE["revealed"]:
                out["question"]["a"] = q["a"]
                out["question"]["exp"] = q["exp"]
        return out

def send_json(handler, obj, status=200):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)

class Handler(BaseHTTPRequestHandler):
    server_version = "Metacomida/2.0"

    def request_base_url(self):
        forced = os.getenv("PUBLIC_URL", "").strip().rstrip("/")
        if forced:
            return forced
        host = self.headers.get("Host", "").strip()
        proto = self.headers.get("X-Forwarded-Proto", "").strip() or "http"
        if host:
            return f"{proto}://{host}".rstrip("/")
        return STATE.get("base_url", "").rstrip("/")

    def presenter_authorized(self, body=None, qs=None):
        pin = ""
        if isinstance(body, dict):
            pin = str(body.get("pin", ""))
        if not pin and isinstance(qs, dict):
            pin = str((qs.get("pin") or [""])[0])
        return pin == PRESENTER_PIN

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/state":
            return send_json(self, public_state(self.request_base_url()))

        if path == "/api/config":
            return send_json(self, {"presenter_pin_required": True})

        if path in ("/", "/presentador", "/host"):
            fp = ROOT / "presentador.html"
        elif path == "/lider":
            fp = ROOT / "lider.html"
        elif path == "/health":
            return send_json(self, {"ok": True})
        else:
            self.send_error(404)
            return

        data = fp.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return send_json(self, {"ok": False, "error":"JSON inválido"}, 400)

        path = urllib.parse.urlparse(self.path).path

        presenter_routes = {"/api/timer","/api/reveal","/api/next","/api/score","/api/reset"}
        if path in presenter_routes and not self.presenter_authorized(body=body):
            return send_json(self, {"ok":False,"error":"PIN de presentador incorrecto"},403)

        if path == "/api/join":
            try:
                team = int(body.get("team")) - 1
            except Exception:
                return send_json(self, {"ok":False,"error":"Equipo inválido"},400)
            if team not in range(4):
                return send_json(self, {"ok":False,"error":"Equipo inválido"},400)
            name = str(body.get("name","")).strip()[:30] or f"Líder {team+1}"
            with LOCK:
                STATE["leaders"][team] = name
            return send_json(self, {"ok":True,"state":public_state(self.request_base_url())})

        if path == "/api/answer":
            try:
                team = int(body.get("team")) - 1
                choice = int(body.get("choice"))
            except Exception:
                return send_json(self, {"ok":False,"error":"Datos inválidos"},400)
            if team not in range(4) or choice not in range(4):
                return send_json(self, {"ok":False,"error":"Datos inválidos"},400)
            with LOCK:
                if STATE["question_index"] >= len(QUESTIONS):
                    return send_json(self, {"ok":False,"error":"Ya terminó la ronda de preguntas"},409)
                if STATE["revealed"]:
                    return send_json(self, {"ok":False,"error":"La respuesta ya fue revelada"},409)
                if STATE["start_time"] is None or STATE["deadline"] is None:
                    return send_json(self, {"ok":False,"error":"Espera a que el presentador inicie el cronómetro"},409)

                now = time.time()
                if now > STATE["deadline"]:
                    return send_json(self, {"ok":False,"error":"Se acabó el tiempo"},409)
                if STATE["submissions"][team] is not None:
                    return send_json(self, {"ok":False,"error":"Tu equipo ya respondió esta pregunta"},409)

                elapsed = max(0.0, now - STATE["start_time"])
                STATE["submissions"][team] = choice
                STATE["response_times"][team] = round(elapsed, 2)
            return send_json(self, {"ok":True})

        if path == "/api/timer":
            with LOCK:
                now = time.time()
                STATE["start_time"] = now
                STATE["deadline"] = now + 15
                STATE["submissions"] = [None,None,None,None]
                STATE["response_times"] = [None,None,None,None]
                STATE["awarded_points"] = [0,0,0,0]
                STATE["awarded"] = False
            return send_json(self, {"ok":True,"state":public_state(self.request_base_url())})

        if path == "/api/reveal":
            with LOCK:
                idx = STATE["question_index"]
                if idx >= len(QUESTIONS):
                    return send_json(self, {"ok":False},409)
                if not STATE["revealed"]:
                    STATE["revealed"] = True
                    if not STATE["awarded"]:
                        correct = QUESTIONS[idx]["a"]
                        for i, choice in enumerate(STATE["submissions"]):
                            points = 0
                            elapsed = STATE["response_times"][i]
                            if choice == correct and elapsed is not None:
                                if elapsed <= 5:
                                    points = 3
                                elif elapsed <= 10:
                                    points = 2
                                elif elapsed <= 15:
                                    points = 1
                                STATE["scores"][i] += points
                            STATE["awarded_points"][i] = points
                        STATE["awarded"] = True
                STATE["deadline"] = None
            return send_json(self, {"ok":True,"state":public_state(self.request_base_url())})

        if path == "/api/next":
            with LOCK:
                if STATE["question_index"] < len(QUESTIONS):
                    STATE["question_index"] += 1
                STATE["revealed"] = False
                STATE["submissions"] = [None,None,None,None]
                STATE["response_times"] = [None,None,None,None]
                STATE["awarded_points"] = [0,0,0,0]
                STATE["awarded"] = False
                STATE["start_time"] = None
                STATE["deadline"] = None
            return send_json(self, {"ok":True,"state":public_state(self.request_base_url())})

        if path == "/api/score":
            try:
                team = int(body.get("team")) - 1
                delta = int(body.get("delta"))
            except Exception:
                return send_json(self, {"ok":False,"error":"Datos inválidos"},400)
            if team not in range(4) or delta not in (-3,-2,-1,1,2,3,5):
                return send_json(self, {"ok":False,"error":"Puntaje inválido"},400)
            with LOCK:
                STATE["scores"][team] += delta
            return send_json(self, {"ok":True,"state":public_state(self.request_base_url())})

        if path == "/api/reset":
            with LOCK:
                STATE["question_index"] = 0
                STATE["revealed"] = False
                STATE["scores"] = [0,0,0,0]
                STATE["submissions"] = [None,None,None,None]
                STATE["response_times"] = [None,None,None,None]
                STATE["awarded_points"] = [0,0,0,0]
                STATE["awarded"] = False
                STATE["start_time"] = None
                STATE["deadline"] = None
            return send_json(self, {"ok":True,"state":public_state(self.request_base_url())})

        return send_json(self, {"ok":False,"error":"Ruta no encontrada"},404)

def make_server():
    port_env = os.getenv("PORT", "").strip()
    if port_env:
        return ThreadingHTTPServer(("0.0.0.0", int(port_env)), Handler)
    for port in range(8080, 8091):
        try:
            return ThreadingHTTPServer(("0.0.0.0", port), Handler)
        except OSError:
            continue
    raise RuntimeError("No encontré un puerto libre entre 8080 y 8090.")

def main():
    server = make_server()
    port = server.server_address[1]
    ip = local_ip()

    public_url = os.getenv("PUBLIC_URL", "").strip().rstrip("/")
    if public_url:
        STATE["base_url"] = public_url
    else:
        STATE["base_url"] = f"http://{ip}:{port}"

    print("="*68)
    print(" METACOMIDA · PRESENTADOR DESDE EL CELULAR")
    print("="*68)
    print(f" Presentador: {STATE['base_url']}/presentador")
    print(f" Líderes:     {STATE['base_url']}/lider")
    print(f" PIN presentador: {PRESENTER_PIN}")
    print("")
    print(" Para uso sin computador, este servidor debe estar publicado en Internet.")
    print(" Define PORT automáticamente con tu plataforma y, opcionalmente, PUBLIC_URL.")
    print("="*68)

    if not os.getenv("PORT"):
        try:
            webbrowser.open(f"http://127.0.0.1:{port}/presentador")
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor cerrado.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
