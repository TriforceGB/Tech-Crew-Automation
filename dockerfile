FROM python:3.12

WORKDIR /bot

COPY main.py /bot
COPY .env /bot
COPY requirements.txt /bot

RUN pip install -r requirements.txt

CMD ["python", "main.py"]

