FROM python:3.7-alpine3.9

RUN mkdir /heavenbot
RUN mkdir /heavenbot/data

VOLUME ["/heavenbot/data"]

WORKDIR /heavenbot

COPY LICENSE .

# pip requirements
COPY requirements.txt .

RUN pip install --cache-dir=pip-cache -r requirements.txt
RUN rm -r pip-cache

# Docker entrypoint
COPY docker/ docker/
RUN chmod +x docker/entrypoint.sh

# Sample config
COPY sample-config.ini .

# Python sources
COPY src/ src/
ENV PYTHONPATH=/heavenbot

ENTRYPOINT ["/heavenbot/docker/entrypoint.sh"]

CMD ["irc3", "-v", "/heavenbot/data/config.ini"]
