FROM python:3.7.10-buster

WORKDIR /app

COPY requirements.txt /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python3", "buynilla.py"]
