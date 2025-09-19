#!/bin/bash
set -euo pipefail

/usr/bin/docker compose -f /root/online_customer/docker-compose.prod.yml run --rm certbot renew >/var/log/online_customer_certbot.log 2>&1
/usr/bin/docker compose -f /root/online_customer/docker-compose.ip.yml exec nginx nginx -s reload >>/var/log/online_customer_certbot.log 2>&1
