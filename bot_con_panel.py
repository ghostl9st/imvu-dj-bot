# bot_con_panel.py - Versión Render CORREGIDA
import os, threading, asyncio
from flask import Flask, render_template_string, request, jsonify
import slixmpp as sleekxmpp
from youtubesearchpython import VideosSearch
from collections import deque

USUARIO_BOT = os.getenv("IMVU_USER", "l9stmusic@chat.imvu.com")
PASSWORD_BOT = os.getenv("IMVU_PASS", "tu_contraseña_bot")
SALA = os.getenv("IMVU_ROOM", "room-381655582-82@conference.chat.imvu.com")
NICK_BOT = os.getenv("IMVU_NICK", "l9stmusic")

app = Flask(__name__)
cola = deque()
actual = {"titulo": "Nada sonando", "link": "", "pedido_por": ""}
bot_instance = None

HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>DJ Panel - IMVU</title>
<style>
body{background:#0f0f1a;color:white;font-family:sans-serif;padding:15px;text-align:center}
.card{background:#1e1e2e;padding:20px;border-radius:15px;margin-bottom:15px}
input{width:80%;padding:12px;border-radius:10px;border:none;margin:10px 0}
button{padding:12px 20px;border:none;border-radius:10px;font-weight:bold;cursor:pointer;margin:5px}
.play{background:#ff0055;color:white;width:85%}
.skip{background:#ffaa00;color:black}
.stop{background:#444;color:white}
.queue{text-align:left;background:#2a2a3a;padding:10px;border-radius:10px}
</style></head>
<body>
<h1>🎵 DJ PANEL IMVU</h1>
<div class="card"><h3>Ahora Sonando</h3><p id="actual">Cargando...</p><a id="link" href="#" target="_blank" style="color:#ff77aa">Abrir en YouTube</a></div>
<div class="card">
<input id="cancion" placeholder="Escribe canción o artista...">
<br><button class="play" onclick="poner()">▶ PONER CANCIÓN</button><br>
<button class="skip" onclick="accion('skip')">⏭ SKIP</button>
<button class="stop" onclick="accion('stop')">⏹ STOP</button>
<button class="skip" onclick="accion('autodj')">🤖 AUTO-DJ</button>
</div>
<div class="card"><h3>Cola</h3><div class="queue" id="cola"></div></div>
<script>
async function refresh(){
 let r = await fetch('/status'); let d = await r.json();
 document.getElementById('actual').innerText = d.actual.titulo + ' - Pedido por: ' + d.actual.pedido_por;
 document.getElementById('link').href = d.actual.link;
 document.getElementById('cola').innerHTML = d.cola.map((c,i)=> (i+1)+'. '+c.titulo).join('<br>') || 'Cola vacía';
}
async function poner(){
 let q = document.getElementById('cancion').value;
 if(!q) return alert('Escribe una canción');
 await fetch('/play', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({q:q, user:'Panel Web'})});
 document.getElementById('cancion').value=''; refresh();
}
async function accion(a){ await fetch('/'+a, {method:'POST'}); refresh(); }
setInterval(refresh, 3000); refresh();
</script></body></html>
"""

@app.route('/')
def index(): return render_template_string(HTML)
@app.route('/status')
def status(): return jsonify({"actual": actual, "cola": list(cola)})
@app.route('/ping')
def ping(): return "Bot vivo!", 200
@app.route('/play', methods=['POST'])
def play_web():
    data = request.json
    agregar_a_cola(data.get('q'), data.get('user', 'Panel Web'))
    return jsonify({"ok": True})
@app.route('/skip', methods=['POST'])
def skip_web():
    siguiente_cancion(); return jsonify({"ok": True})
@app.route('/stop', methods=['POST'])
def stop_web():
    global actual
    cola.clear(); actual = {"titulo": "Nada sonando", "link": "", "pedido_por": ""}
    if bot_instance: bot_instance.send_message(mto=SALA, mbody="⏹ Música detenida desde el Panel Web", mtype='groupchat')
    return jsonify({"ok": True})
@app.route('/autodj', methods=['POST'])
def autodj_web():
    agregar_a_cola("Bad Bunny - Tití Me Preguntó", "Auto-DJ")
    agregar_a_cola("Karol G - Provenza", "Auto-DJ")
    agregar_a_cola("Feid - Hey Mor", "Auto-DJ")
    return jsonify({"ok": True})

def buscar_youtube(query):
    try:
        r = VideosSearch(query, limit=1).result()['result'][0]
        return {"titulo": r['title'], "link": r['link']}
    except: return None

def agregar_a_cola(query, usuario):
    cancion = buscar_youtube(query)
    if not cancion: return
    cancion["pedido_por"] = usuario
    if actual["titulo"] == "Nada sonando": poner_actual(cancion)
    else:
        cola.append(cancion)
        if bot_instance: bot_instance.send_message(mto=SALA, mbody=f"🎵 Agregado a la cola: {cancion['titulo']} - Pedido por {usuario}", mtype='groupchat')

def poner_actual(c
