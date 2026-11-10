import os, threading, asyncio
from flask import Flask, request, jsonify
import slixmpp as sleekxmpp
from youtubesearchpython import VideosSearch
from collections import deque

USUARIO_BOT = os.getenv("IMVU_USER", "l9stmusic@chat.imvu.com")
PASSWORD_BOT = os.getenv("IMVU_PASS", "")
SALA = os.getenv("IMVU_ROOM", "room-381655582-82@conference.chat.imvu.com")
NICK_BOT = os.getenv("IMVU_NICK", "l9stmusic")
app = Flask(__name__)
cola = deque()
actual = {"titulo": "Nada sonando", "link": "", "pedido_por": ""}
bot_instance = None

@app.route('/')
def index():
    return "Bot DJ corriendo - Cola: " + str(len(cola))

@app.route('/status')
def status():
    return jsonify({"actual": actual, "cola": list(cola)})

@app.route('/play', methods=['POST'])
def play_web():
    d = request.json
    agregar_a_cola(d.get('q'), d.get('user', 'Panel'))
    return jsonify({"ok": True})

@app.route('/skip', methods=['POST'])
def skip_web():
    siguiente_cancion()
    return jsonify({"ok": True})

@app.route('/stop', methods=['POST'])
def stop_web():
    global actual
    cola.clear()
    actual = {"titulo": "Nada sonando", "link": "", "pedido_por": ""}
    return jsonify({"ok": True})

def buscar_youtube(q):
    try:
        r = VideosSearch(q, limit=1).result()['result'][0]
        return {"titulo": r['title'], "link": r['link']}
    except:
        return None

def agregar_a_cola(q, usuario):
    cancion = buscar_youtube(q)
    if not cancion:
        return
    cancion["pedido_por"] = usuario
    if actual["titulo"] == "Nada sonando":
        poner_actual(cancion)
    else:
        cola.append(cancion)
        if bot_instance:
            bot_instance.send_message(mto=SALA, mbody="Agregado: " + cancion['titulo'], mtype='groupchat')

def poner_actual(cancion):
    global actual
    actual = cancion
    if bot_instance:
        bot_instance.send_message(mto=SALA, mbody="Ahora sonando: " + cancion['titulo'] + " | " + cancion['link'], mtype='groupchat')

def siguiente_cancion():
    global actual
    if cola:
        poner_actual(cola.popleft())
    else:
        actual = {"titulo": "Nada sonando", "link": "", "pedido_por": ""}

class MusicBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.mensaje)
        self.add_event_handler("failed_auth", self.auth_fallida)
        self.register_plugin('xep_0045')
        self.register_plugin('xep_0199')
    def auth_fallida(self, event):
        print(">>> AUTH FALLIDA", flush=True)
    async def start(self, event):
        print(">>> CONECTADO, ENTRANDO A SALA...", flush=True)
        await self.get_roster()
        self.send_presence()
        await self.plugin['xep_0045'].join_muc(SALA, NICK_BOT, wait=True)
        print(">>> YA ENTRE A LA SALA", flush=True)
        self.send_message(mto=SALA, mbody="DJ Bot conectado! !play cancion | !cola | !skip", mtype='groupchat')
    def mensaje(self, msg):
        if msg['type'] not in ('groupchat', 'chat'):
            return
        try:
            nick = msg['mucnick']
        except:
            nick = str(msg['from']).split('/')[-1]
        if nick == NICK_BOT:
            return
        texto = msg['body'].strip()
        print(">>> MENSAJE", nick, texto, flush=True)
        if texto.lower().startswith("!play "):
            agregar_a_cola(texto[6:], nick)
        elif texto.lower() == "!skip":
            siguiente_cancion()
        elif texto.lower() == "!cola":
            lista = "Cola vacia"
            if cola:
                lista = ""
                for i, c in enumerate(cola):
                    lista = lista + str(i+1) + ". " + c['titulo'] + "\n"
            self.send_message(mto=SALA, mbody=lista, mtype='groupchat')

def correr_bot():
    global bot_instance
    print(">>> INICIANDO BOT", USUARIO_BOT, SALA, flush=True)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_instance = MusicBot(USUARIO_BOT, PASSWORD_BOT)
    bot_instance.connect(address=('chat.imvu.com', 5222))
    bot_instance.process(forever=False)

if __name__ == '__main__':
    threading.Thread(target=correr_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
