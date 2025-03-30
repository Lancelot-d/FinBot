FROM python:3.12.4-slim-bullseye

COPY ./app /app
WORKDIR /app
RUN set -ex && \
    pip install -r requirements.txt
EXPOSE 8070/tcp

CMD ["gunicorn","-w" ,"1","--timeout","360","--bind" ,"0.0.0.0:8070", "app:server"]