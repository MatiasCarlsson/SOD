FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY src/sensors/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/common/ ./src/common/
COPY src/sensors/ ./src/sensors/

CMD ["python", "-m", "src.sensors.sensor_simulator"]

