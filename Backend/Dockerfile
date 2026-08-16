FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /code

COPY pyproject.toml ./
COPY src ./src
COPY skills ./skills
COPY knowledge-store ./knowledge-store
COPY tests ./tests
COPY entrypoint.sh worker-entrypoint.sh ./
RUN pip install --no-cache-dir -e ".[dev]"
RUN chmod +x entrypoint.sh worker-entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
