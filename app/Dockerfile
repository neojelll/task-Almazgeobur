FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    cargo \
    git \
    && rm -rf /var/lib/apt/lists/*
	
RUN pip install --no-cache-dir poetry
	
COPY pyproject.toml poetry.lock ./

	
RUN poetry install --no-root --no-dev
	
COPY . .

ENTRYPOINT ["poetry", "run"]

CMD ["run-app"]
