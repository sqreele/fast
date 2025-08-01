#!/bin/bash

# Quick Admin Interface Fix for Production
# Run this on the production server: 206.189.89.239

echo "🔧 Quick Admin Interface Fix"
echo "Server: $(hostname -I | awk '{print $1}')"
echo "Date: $(date)"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found"
    echo "Please run this script from the PM System project root directory"
    exit 1
fi

echo "📁 Found docker-compose.prod.yml - proceeding with fix..."

# Check if nginx config has the admin route
if grep -q "location /admin" nginx/nginx.prod.conf; then
    echo "✅ Admin route already exists in nginx configuration"
else
    echo "❌ Admin route missing - this needs to be added manually"
    echo ""
    echo "Please add this to nginx/nginx.prod.conf before the 'location /' block:"
    echo ""
    echo "        # Admin dashboard - proxy to FastAPI SQLAlchemy Admin"
    echo "        location /admin {"
    echo "            proxy_pass http://fastapi_backend;"
    echo "            proxy_set_header Host \$host;"
    echo "            proxy_set_header X-Real-IP \$remote_addr;"
    echo "            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
    echo "            proxy_set_header X-Forwarded-Proto \$scheme;"
    echo "            add_header Cache-Control \"no-cache, no-store, must-revalidate\";"
    echo "            proxy_connect_timeout 60s;"
    echo "            proxy_send_timeout 60s;"
    echo "            proxy_read_timeout 60s;"
    echo "        }"
    echo ""
    exit 1
fi

# Restart nginx to apply the configuration
echo "🔄 Restarting nginx to apply configuration..."
if docker-compose -f docker-compose.prod.yml restart nginx; then
    echo "✅ Nginx restarted successfully"
else
    echo "❌ Failed to restart nginx"
    echo "Try: docker-compose -f docker-compose.prod.yml logs nginx"
    exit 1
fi

# Wait a moment for nginx to fully start
sleep 5

# Test the admin interface
echo "🧪 Testing admin interface..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/ 2>/dev/null)

if [ "$response" = "200" ] || [ "$response" = "301" ] || [ "$response" = "302" ]; then
    echo "✅ Admin interface is now accessible!"
    echo "🌐 URL: http://206.189.89.239/admin/"
elif [ "$response" = "404" ]; then
    echo "❌ Still getting 404 - backend may not be running"
    echo "Check FastAPI container: docker-compose -f docker-compose.prod.yml logs fastapi"
else
    echo "⚠️  Got HTTP $response - check logs for details"
fi

echo ""
echo "🎯 Admin Interface Features:"
echo "   - User Management"
echo "   - Property Management"
echo "   - Room & Machine Management"
echo "   - Work Orders & Maintenance"
echo "   - PM Schedules & Inspections"
echo "   - File Management"
echo ""
echo "✅ Fix completed!"