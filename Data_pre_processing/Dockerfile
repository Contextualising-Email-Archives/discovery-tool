FROM python:3.7.13-slim

RUN apt-get update \
    && apt-get install -y wget \
    && apt-get clean

WORKDIR /opt
RUN wget https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz
RUN tar -zxvf enron_mail_20150507.tar.gz

ENV PIP_VERSION=22.0.4
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /srv
COPY requirements.txt .
RUN pip install -U pip==$PIP_VERSION
RUN pip install -r requirements.txt
COPY Enron_data.py .

VOLUME ["/srv", "/opt"]

ENTRYPOINT ["python", "Enron_data.py", "/opt/", "2", "/srv/"]