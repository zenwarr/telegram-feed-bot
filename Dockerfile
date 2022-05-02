FROM python:3.10.2-alpine3.15

ADD ./src/requirements.txt /src/requirements.txt

RUN cd /src && pip install -r requirements.txt

ADD ./src /src

USER 1000

ENTRYPOINT [ "python", "-u", "/src/main.py" ]
