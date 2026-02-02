# Certbot Initial - Standalone mode for first certificate
FROM certbot/certbot:latest

COPY certbot-initial-entrypoint.sh /certbot-initial-entrypoint.sh

RUN chmod +x /certbot-initial-entrypoint.sh

ENTRYPOINT ["/certbot-initial-entrypoint.sh"]
