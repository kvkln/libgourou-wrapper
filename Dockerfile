FROM docker.io/bcliang/docker-libgourou

RUN adduser --no-create-home --disabled-password libgourou-wrapper

WORKDIR /app
EXPOSE 8080/tcp
ENV PYTHONUNBUFFERED=True

COPY requirements.txt ./requirements.txt
RUN apk update --no-cache && \
    apk add --no-cache python3 py3-pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del --no-cache py3-pip

COPY server.py ./server.py
COPY index.html ./www/index.html

USER libgourou-wrapper

ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080", "--no-server-header"]
