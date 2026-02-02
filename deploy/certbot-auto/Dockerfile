# Certbot Auto - Webroot mode for certificate renewals
FROM certbot/certbot:latest

COPY certbot-auto-entrypoint.sh /certbot-auto-entrypoint.sh

RUN chmod +x /certbot-auto-entrypoint.sh

ENTRYPOINT ["/certbot-auto-entrypoint.sh"]
