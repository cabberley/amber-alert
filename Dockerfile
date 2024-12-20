FROM python:3.13.1-alpine3.20

WORKDIR /opt/amber

RUN apk add --no-cache supercronic \
    && addgroup -S amber && adduser -S amber -G amber \
    && mkdir -p data \
    && chown amber:amber data \
    && apk --no-cache upgrade \
    && apk add --no-cache tzdata

USER amber

COPY amber-cron ./crontab/amber-cron
COPY app.py app.py
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=australia\Brisbane \
    AMBER_SITE_ID= \
    AMBER_API_KEY= \
    HOME_ASSISTANT_URI= \
    HOME_ASSISTANT_BEARER= \
    AMBER_FEED_IN_PRICE_SENSOR= \
    AMBER_GENERAL_PRICE_SENSOR= \
    AMBER_PRICE_DATE_SENSOR= \
    ALERT_HIGH=25 \
    ALERT_LOW=10 \
    DATA_RES=30

VOLUME ["/opt/amber/data"]

ENTRYPOINT ["supercronic", "./crontab/amber-cron"]

LABEL org.opencontainers.image.authors="cabberley <chris@abberley.com.au>"
