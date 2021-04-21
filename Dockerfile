FROM python

RUN pip install lnetatmo netatmo influxdb

RUN apt-get update && apt-get install -y cron 
