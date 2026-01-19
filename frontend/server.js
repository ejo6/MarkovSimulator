import http from "http";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.join(__dirname, "public");
const apiHost = process.env.MARKOV_API_HOST || "localhost";
const apiPort = process.env.MARKOV_API_PORT || "8000";

function sendFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Not found");
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const contentType = ext === ".css" ? "text/css" : ext === ".js" ? "text/javascript" : "text/html";
    res.writeHead(200, { "Content-Type": contentType });
    res.end(data);
  });
}

function proxyRun(req, res) {
  const options = {
    host: apiHost,
    port: apiPort,
    path: "/run",
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }
  };

  const upstream = http.request(options, upstreamRes => {
    let body = "";
    upstreamRes.on("data", chunk => { body += chunk; });
    upstreamRes.on("end", () => {
      res.writeHead(upstreamRes.statusCode || 500, { "Content-Type": "application/json" });
      res.end(body);
    });
  });

  upstream.on("error", () => {
    res.writeHead(502, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Failed to reach API" }));
  });

  let body = "";
  req.on("data", chunk => { body += chunk; });
  req.on("end", () => { upstream.end(body); });
}

function proxyChart(req, res) {
  const url = new URL(req.url, "http://localhost");
  const options = {
    host: apiHost,
    port: apiPort,
    path: url.pathname.replace("/api", "") + url.search,
    method: "GET"
  };

  const upstream = http.request(options, upstreamRes => {
    res.writeHead(upstreamRes.statusCode || 500, upstreamRes.headers);
    upstreamRes.pipe(res);
  });

  upstream.on("error", () => {
    res.writeHead(502, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Failed to reach API" }));
  });

  upstream.end();
}

const server = http.createServer((req, res) => {
  if (req.url === "/api/run" && req.method === "POST") {
    proxyRun(req, res);
    return;
  }
  if (req.url.startsWith("/api/chart") && req.method === "GET") {
    proxyChart(req, res);
    return;
  }

  const urlPath = req.url === "/" ? "/index.html" : req.url;
  const safePath = path.normalize(urlPath).replace(/^\.\.(\/|\\)/, "");
  const filePath = path.join(publicDir, safePath);
  sendFile(res, filePath);
});

server.listen(3000, () => {
  console.log("Frontend running on http://localhost:3000");
});
