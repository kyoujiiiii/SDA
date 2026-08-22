FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY back/requirements.txt /app/back/requirements.txt
COPY core/ /app/core/

RUN pip install --no-cache-dir -r back/requirements.txt \
    && python -m spacy download en_core_web_lg

COPY back/ /app/back/

WORKDIR /app/back

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
