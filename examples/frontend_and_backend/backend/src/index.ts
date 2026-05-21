import { configDotenv } from "dotenv";
import express from "express";

configDotenv({ quiet: true });

const app = express();

app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  console.log(req.method, req.url, res.statusCode);
  next();
});

app.get("/", (_, res) => {
  res.send("Hello World");
});

const port = process.env.PORT;
if (!port) {
  throw new Error("PORT environment variable not set");
}

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
