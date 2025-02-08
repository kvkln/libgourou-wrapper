# libgourou-wrapper
A wrapper for libgourou to convert DRM protected Ebooks to epub.

## Deployment

```yaml
services:
  libgourou-wrapper:
    image: ghcr.io/kvkln/libgourou-wrapper:edge
    restart: always
    hostname: libgourou-wrapper
    mem_limit: 300m
    memswap_limit: 300m
    cpus: 2
    ports:
      - 8080:8080
```

## Build

```bash
# build the Docker file
docker build -t libgourou-wrapper:latest .

# start the container
docker run -p 8080:8080 libgourou-wrapper:latest
```
