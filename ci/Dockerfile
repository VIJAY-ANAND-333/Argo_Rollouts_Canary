FROM python:3.9-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 9000

CMD ["gunicorn", "--bind", "0.0.0.0:9000", "app:app"]
