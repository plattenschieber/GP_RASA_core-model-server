# Model-Server for Core
HTTP-Server der das Modell für den Rasa-Core bereitstellt. Das Modell wird trainiert und dann als zip auf dem port 8000 zur Verfügung gestellt.

## Docker
Für die Verwendung in Docker sind folgende Befehle anzuwenden:
```bash
docker build -t chatbot-model-server .
```
```bash
docker-compose -p gpb -f ./docker/docker-compose.yaml up
```

## Testanfragen
```bash
GET http://localhost:8000/models
```
Wenn der Header "If-None-Match" mit der richtigen Version gesetzt ist kommt 204 No Content zurück, in allen anderen fällen 200 mit ddem content-type: application/zip


