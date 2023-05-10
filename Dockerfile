FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


EXPOSE 5001

CMD ["gunicorn", "--workers", "8","--bind", "0.0.0.0:8585", "wsgi:app"]
