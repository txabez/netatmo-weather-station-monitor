#!/bin/sh
touch /var/log/cron.log
crontab /etc/cron.d/netatmo
cron -f
