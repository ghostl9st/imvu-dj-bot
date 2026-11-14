
const http = require("http");

const PORT = process.env.PORT || 3000;

function responder(comando) {
  switch (comando.toLowerCase().trim()) {
    case "!hola":
      return "🎧 DJ l9st: ¡Bienvenidos a la sala!";
    case "!play":
      return "🎶 DJ l9st: ¡Preparados para la música!";
    case "!pausa":
      return "⏸️ DJ l9st: Pausa solicitada.";
    case "!dj":
      return "🔥 ¡Estás escuchando a DJ l9st!";
    case "!comandos":
      return "Comandos: !hola, !play, !pausa, !dj";
    default:
      return "❓ Comando no reconocido. Escribe !comandos";
  }
}

const server = http.createServer((req, res) => {
  res.setHeader("Content-Type", "application/json");

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
          bot: "DJ l9st",
          respuesta: responder(data.command || "")
        }));
      } catch {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: "Datos inválidos" }));
      }
    });
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ error: "No encontrado" }));
});

server.listen(PORT, () => {
  console.log("🎧 DJ l9st está encendido");
});
