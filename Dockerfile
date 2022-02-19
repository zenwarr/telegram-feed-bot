FROM python:3.10.2-alpine3.15

ADD ./src /app

RUN cd /app && pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "/app/main.py" ]
