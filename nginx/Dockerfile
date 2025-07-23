FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Remove default nginx configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY default.conf /etc/nginx/conf.d/default.conf

# Create directory for static files
RUN mkdir -p /var/www/static

# Set proper permissions (nginx user already exists in base image)
RUN chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    chown -R nginx:nginx /var/www

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 