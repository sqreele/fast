FROM nginx:1.25-alpine

# Install additional packages
RUN apk add --no-cache \
    curl \
    openssl \
    logrotate \
    tzdata \
    bash

# Create nginx user
RUN addgroup -g 1001 -S nginx && \
    adduser -u 1001 -D -S -G nginx nginx

# Remove default config
RUN rm -f /etc/nginx/conf.d/default.conf \
    && rm -f /etc/nginx/nginx.conf

# Create required directories and set permissions
RUN mkdir -p \
    /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp \
    /var/log/nginx \
    /etc/nginx/ssl \
    /var/www/static \
    /etc/nginx/conf.d \
    && chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx /var/www

# Copy nginx config files
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf security-headers.conf gzip.conf /etc/nginx/conf.d/

# Generate self-signed cert for local HTTPS
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
    && chmod 600 /etc/nginx/ssl/nginx-selfsigned.key \
    && chmod 644 /etc/nginx/ssl/nginx-selfsigned.crt \
    && chown -R nginx:nginx /etc/nginx/ssl

# Copy entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Configure logrotate
RUN echo '/var/log/nginx/*.log {\n\
    daily\n\
    missingok\n\
    rotate 52\n\
    compress\n\
    delaycompress\n\
    notifempty\n\
    create 644 nginx nginx\n\
    postrotate\n\
        if [ -f /var/run/nginx.pid ]; then\n\
            kill -USR1 `cat /var/run/nginx.pid`\n\
        fi\n\
    endscript\n\
}' > /etc/logrotate.d/nginx

# Expose HTTP & HTTPS
EXPOSE 80 443

# Health check (make sure /health exists or adjust accordingly)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start the container
CMD ["/docker-entrypoint.sh"]
