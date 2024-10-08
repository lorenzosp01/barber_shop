FROM python:3.8-buster

ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt


COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]