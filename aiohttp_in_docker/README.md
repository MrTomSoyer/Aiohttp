# Aiohttp in docker

Для запуска проекта необходимо:
- Создание контейнера
```bash
docker compose -f aiohttp_in_docker/docker-compose.aiohttp.yml up --build -d   
```
- С помощью [aiohttp_client.py](../aiohttp/aiohttp_client.py) делать соответсвующие запросы