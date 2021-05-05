FROM python:3.7.10-buster

WORKDIR /app

COPY requirements.txt /app

COPY pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python3", "code.py"]
