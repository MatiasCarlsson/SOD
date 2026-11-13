FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY src/collector/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/common/ ./src/common/
COPY src/collector/ ./src/collector/

CMD ["python", "-m", "src.collector.collector"]

