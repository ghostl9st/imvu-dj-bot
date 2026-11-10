import os, threading, asyncio
from flask import Flask
from slixmpp import ClientXMPP

print(">>> ARCHIVO CARGADO - VERSION NUEVA", flush=True)

USUARIO = os.getenv("IMVU_USER", "l9stmusic@chat.imvu.com")
CLAVE = os.getenv("IMVU_PASS", "")
SALA = os.getenv("IMVU_ROOM", "room-381655582-82@conference.chat.imvu.com")
NICK = os.getenv("IMVU_NICK", "l9stmusic")

app = Flask(__name__)
cola = []

class Bot(ClientXMPP):
    def __init__(self, jid, password, room, nick):
        super().__init__(jid, password)
        self.room = room
        self.nick = nick
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("failed_auth", self.fallo_auth)
        self.add_event_handler("disconnected", self.desconectado)
        self.add_event_handler("groupchat_message", self.mensaje)
        self.register_plugin('xep_0045')
        self.register_plugin('xep_0199')

    async def start(self, event):
        print(">>> CONECTADO, ENTRANDO A SALA...", flush=True)
        self.send_presence()
        await self.get_roster()
        self.plugin['xep_0045'].join_muc(self.room, self.nick)
        print(">>> YA ENTRE A LA SALA", flush=True)
        self.send_message(mto=self.room, mbody="DJ Bot conectado!", mtype='groupchat')

    def fallo_auth(self, event):
        print(">>> ERROR: AUTH FALLIDA", flush=True)

    def desconectado(self, event):
        print(">>> ERROR: SE DESCONECTO - CUENTA DUPLICADA", flush=True)

    def mensaje(self, msg):
        if msg['mucnick'] == self.nick:
            return
        texto = str(msg['body']).strip()
        print(f">>> MENSAJE: {texto}", flush=True)
        if texto.lower().startswith("!play "):
            cancion = texto[6:].strip()
            cola.append(cancion)
            self.send_message(mto=self.room, mbody=f"Ahora sonando: {cancion}", mtype='groupchat')

@app.route("/")
def home():
    return f"Bot DJ corriendo - Cola: {len(cola)}"

def correr_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    print(f">>> INICIANDO BOT {USUARIO}", flush=True)
    print(f">>> CLAVE TIENE {len(CLAVE)} CARACTERES", flush=True)
    bot = Bot(USUARIO, CLAVE, SALA, NICK)
    bot.connect(address=('chat.imvu.com', 5222))
    bot.process(forever=True)

if __name__ == "__main__":
    t = threading.Thread(target=correr_bot, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
