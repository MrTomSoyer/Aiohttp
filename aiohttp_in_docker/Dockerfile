FROM python:3.14-slim
WORKDIR /app
COPY aiohttp_in_docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY aiohttp_in_docker/. .
EXPOSE 8080
CMD ["python", "aiohttp_server_in_docker.py"]
