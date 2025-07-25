FROM nginx:1.25-alpine

# Install additional packages
RUN apk add --no-cache \
    curl \
    openssl \
    logrotate \
    tzdata \
    bash

# Create nginx user and group only if not already existing
RUN getent group nginx || addgroup -g 1001 -S nginx && \
    id -u nginx || adduser -u 1001 -D -S -G nginx nginx

# Remove default nginx configuration
RUN rm -f /etc/nginx/conf.d/default.conf \
    && rm -f /etc/nginx/nginx.conf

# Create required directories and assign permissions
RUN mkdir -p \
    /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp \
    /var/log/nginx \
    /etc/nginx/ssl \
    /var/www/static \
    /etc/nginx/conf.d && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx /var/www

# Copy custom nginx configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf security-headers.conf gzip.conf /etc/nginx/conf.d/

# Generate self-signed SSL certificate for local development
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" && \
    chmod 600 /etc/nginx/ssl/nginx-selfsigned.key && \
    chmod 644 /etc/nginx/ssl/nginx-selfsigned.crt && \
    chown -R nginx:nginx /etc/nginx/ssl

# Copy custom entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Configure log rotation for nginx logs
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

# Expose standard HTTP and HTTPS ports
EXPOSE 80 443

# Healthcheck (make sure /health exists or modify as needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start the container using custom entrypoint
CMD ["/docker-entrypoint.sh"]
