FROM python:3.10.2-alpine3.15

ADD ./src/requirements.txt /app/requirements.txt

RUN cd /app && pip install -r requirements.txt

ADD ./src /app

USER 1000

ENTRYPOINT [ "python", "-u", "/app/main.py" ]
