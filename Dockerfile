FROM python:3.10.2-alpine3.15

ADD ./src/requirements.txt /app/src/requirements.txt

RUN cd /app/src && pip install -r requirements.txt

ADD ./src /app/src

USER 1000

ENV PYTHONPATH "${PYTHONPATH}:/app"

ENTRYPOINT [ "python", "-u", "/app/src/main.py" ]
