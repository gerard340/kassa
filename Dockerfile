# Kassa - Flask-app achter gunicorn (Caddy doet TLS en proxy).
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 3004

# --preload: app 1x importeren in de master voor het forken, zodat schema-aanmaak
# en het seeden van de demodata niet door twee workers tegelijk gebeuren.
CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:3004", "--workers", "2", "--threads", "4", \
     "--access-logfile", "-", "app:app"]
