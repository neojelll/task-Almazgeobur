FROM python:3.12-alpine

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-dev

RUN poetry run gigachain install-rus-certs

COPY . .

ENTRYPOINT ["poetry", "run"]

CMD ["run-app"]
