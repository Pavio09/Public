FROM python:3.12

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    PORT=8000

COPY . .

RUN pip install --upgrade pip --no-cache-dir && \
    pip install poetry --no-cache-dir && \
    poetry export --without-hashes --format=requirements.txt --output requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

HEALTHCHECK CMD nc -z localhost $PORT

EXPOSE $PORT

CMD ["python", "manage.py", "runserver", "0.0.0.0:$PORT"]