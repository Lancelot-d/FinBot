FROM python:3.10.6-slim-bullseye

COPY ./app /app
COPY ./run.sh /app/run.sh 
WORKDIR /app

RUN set -ex && \
    chmod +x run.sh && \
    pip install -r requirements.txt

EXPOSE 8070/tcp

CMD ["./run.sh"]