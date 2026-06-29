
FROM python:3.11-slim

LABEL description="System health monitor - CI/CD prototype"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

CMD ["python", "app/monitor.py"]