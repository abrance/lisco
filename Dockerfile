# Copy the rest of the application, excluding files listed in .gitignore
# Use a multi-stage build to filter files based on .gitignore
FROM python:3.10-slim-bookworm AS builder
WORKDIR /app

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y gcc ssh default-libmysqlclient-dev vim git gettext libjpeg-dev zlib1g-dev wget make

COPY manifest/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM builder AS final
WORKDIR /app
COPY . .

CMD ["PYTHONPATH=/app python lisco/main.py"]
