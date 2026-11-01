# Aiohttp

Для запуска проекта необходимо:
- Создание контейнера для работы БД
```bash
docker compose -f aiohttp/docker-compose.yaml up --build -d   
```
- Запустить [aiohttp_server.py](aiohttp_server.py)
```bash
python aiohttp/aiohttp_server.py  
```
-С помощью [aiohttp_client.py](aiohttp_client.py) делать соответсвующие запросы