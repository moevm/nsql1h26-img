FROM python:3.12.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY requirements.txt .

RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --no-create-home appuser

USER appuser

CMD ["python", "main.py"]