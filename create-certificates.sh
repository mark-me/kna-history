#!/bin/bash

# Run Certbot to obtain/renew SSL certificates
certbot certonly --standalone --non-interactive --agree-tos -m your@email.com -d yourdomain.com

# Start your application
exec "$@"
