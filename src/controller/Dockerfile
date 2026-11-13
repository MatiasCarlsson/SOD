FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY src/controller/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/common/ ./src/common/
COPY src/controller/ ./src/controller/

CMD ["python", "-m", "src.controller.controller"]

