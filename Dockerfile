FROM alpine:3.22.2 AS builder

RUN apk add g++ pugixml-dev openssl-dev curl-dev libzip-dev make bash git

WORKDIR /usr/src

RUN git clone https://forge.soutade.fr/soutade/libgourou.git \
  && cd libgourou \
  && git clone https://forge.soutade.fr/soutade/uPDFParser lib/updfparser \
  && cd lib/updfparser \
  && make BUILD_STATIC=1 BUILD_SHARED=0 \
  && cd ../.. \
  && make BUILD_STATIC=1



FROM alpine:3.22.2

COPY --from=builder /usr/src/libgourou/utils/acsmdownloader \
                    /usr/src/libgourou/utils/adept_activate \
                    /usr/src/libgourou/utils/adept_remove \
                    /usr/local/bin/

RUN adduser --no-create-home --disabled-password gourou

WORKDIR /app
EXPOSE 8080/tcp
ENV PYTHONUNBUFFERED=True

COPY requirements.txt ./requirements.txt
RUN apk update --no-cache && \
    apk add --no-cache libcurl libzip pugixml python3 py3-pip && \
    pip install --no-cache-dir -r requirements.txt --break-system-packages && \
    apk del --no-cache py3-pip

COPY server.py ./server.py
COPY index.html ./www/index.html

USER gourou

ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080", "--no-server-header", "--ws", "none"]
