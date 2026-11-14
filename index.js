
const http = require("http");

const PORT = process.env.PORT || 3000;

function responder(command) {
  const comandos = {
    "!hola": "🎧 DJ l9st: ¡Bienvenidos!",
    "!play": "🎶 ¡Que comience la música!",
    "!pausa": "⏸️ Pausa solicitada.",
    "!dj": "🔥 ¡Estás escuchando a DJ l9st!",
    "!comandos": "🎵 !hola !play !pausa !dj !comandos"
  };

  return comandos[command.toLowerCase().trim()]
    || "Comando desconocido. Escribe !comandos";
}

const server = http.createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Content-Type", "application/json");

  if (req.method === "OPTIONS") {
    res.end();
    return;
  }

  if (req.method === "GET" && req.url === "/") {
    res.end(JSON.stringify({
      bot: "DJ l9st",
      estado: "Encendido 🎧"
    }));
    return;
  }

  if (req.method === "POST" && req.url === "/command") {
    let body = "";

    req.on("data", chunk => body += chunk);

    req.on("end", () => {
      try {
        const data = JSON.parse(body);
        res.end(JSON.stringify({
          respuesta: responder(data.command || "")
        }));
      } catch {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: "JSON inválido" }));
      }
    });
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ error: "No encontrado" }));
});

server.listen(PORT, () => {
  console.log("DJ l9st encendido 🎧");
});
