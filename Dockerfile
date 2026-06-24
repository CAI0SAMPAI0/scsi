FROM python:3.13-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# Comando para rodar o Django usando Gunicorn ou o runserver nativo exposto na porta 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
