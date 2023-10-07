FROM python:3.11.6-alpine3.18 as builder

ENV PYTHONUNBUFFERED=1
RUN pip install poetry && poetry config virtualenvs.in-project true

WORKDIR /app
ADD pyproject.toml poetry.lock /app/
RUN cd /app && poetry install

FROM python:3.11.6-alpine3.18

ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
COPY --from=builder /app/.venv /app/.venv
USER 1000

ENTRYPOINT [ "/app/.venv/bin/python", "-u", "/app/main.py" ]
