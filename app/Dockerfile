FROM python:3.9.18-slim-bookworm

RUN apt-get update && apt-get install -y certbot
RUN apt-get install -y libmariadb-dev pkg-config python3-dev default-libmysqlclient-dev build-essential apache2 apache2-dev

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN chmod +x /app/create-certificates.sh

EXPOSE 5000

#ENTRYPOINT ["/app/create-certificates.sh"]
ENV FLASK_APP=app.py
#CMD ["gunicorn", "--certfile", "cert.pem", "--keyfile", "key.pem","--bind", "0.0.0.0:5000", "wsgi:app"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
