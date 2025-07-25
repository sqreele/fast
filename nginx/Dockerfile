FROM nginx:1.25-alpine

# Install additional packages for security and monitoring
RUN apk add --no-cache \
    curl \
    openssl \
    logrotate \
    tzdata \
    bash

# Create nginx user and set permissions
RUN addgroup -g 1001 -S nginx || true && \
    adduser -u 1001 -D -S -G nginx nginx || true

# Remove default nginx configuration
RUN rm -f /etc/nginx/conf.d/default.conf \
    && rm -f /etc/nginx/nginx.conf

# Create necessary directories
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
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /etc/nginx \
    && chown -R nginx:nginx /var/www

# Copy custom nginx configurations
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf
COPY security-headers.conf /etc/nginx/conf.d/security-headers.conf
COPY gzip.conf /etc/nginx/conf.d/gzip.conf

# Generate self-signed certificate for development
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set proper permissions for SSL certificates
RUN chmod 600 /etc/nginx/ssl/nginx-selfsigned.key \
    && chmod 644 /etc/nginx/ssl/nginx-selfsigned.crt \
    && chown -R nginx:nginx /etc/nginx/ssl

# Copy and setup startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create log rotation configuration
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

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx (nginx will drop privileges automatically)
CMD ["/docker-entrypoint.sh"] 