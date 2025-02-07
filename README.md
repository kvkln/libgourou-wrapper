# libgourou-wrapper
A wrapper for libgourou to convert DRM protected Ebooks to epub.

## Usage

```bash
# build the Docker file
docker build -t libgourou-wrapper:latest .

# start the container
docker run -p 8080:8080 libgourou-wrapper:latest
```
