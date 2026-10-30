FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install ".[eval,obs]"

COPY data ./data
COPY evals ./evals

ENTRYPOINT ["python", "-m", "kh_graphrag"]
CMD ["--help"]
