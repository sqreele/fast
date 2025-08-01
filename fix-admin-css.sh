#!/bin/bash

echo "🔧 Fixing Admin CSS Issue"
echo "========================"

echo "ℹ️  Issue: Admin static files (/admin/statics/) were being routed to Next.js instead of FastAPI"
echo "✅ Fix: Added specific nginx location block for /admin/statics/ to route to FastAPI backend"
echo ""

echo "📝 Changes made:"
echo "  - Added /admin/statics/ location block in nginx.prod.conf"
echo "  - Added /admin/statics/ location block in default.conf"
echo "  - Both configs now properly route admin static files to FastAPI"
echo ""

echo "🚀 Rebuilding and restarting nginx container..."

# Check if using Docker Compose
if [ -f "docker-compose.prod.yml" ]; then
    echo "📦 Using docker-compose.prod.yml..."
    
    # Rebuild nginx container
    echo "🔨 Rebuilding nginx container..."
    docker-compose -f docker-compose.prod.yml build nginx
    
    # Restart nginx container
    echo "🔄 Restarting nginx container..."
    docker-compose -f docker-compose.prod.yml restart nginx
    
    echo "✅ Nginx container rebuilt and restarted!"
else
    echo "❌ docker-compose.prod.yml not found"
    exit 1
fi

echo ""
echo "🧪 Testing the fix..."
sleep 5

# Test admin page
echo "Testing admin page..."
curl -s -o /dev/null -w "Admin page: %{http_code}\n" http://206.189.89.239/admin/

# Test CSS files
echo "Testing CSS files..."
curl -s -o /dev/null -w "tabler.min.css: %{http_code}\n" http://206.189.89.239/admin/statics/css/tabler.min.css
curl -s -o /dev/null -w "main.css: %{http_code}\n" http://206.189.89.239/admin/statics/css/main.css
curl -s -o /dev/null -w "fontawesome.min.css: %{http_code}\n" http://206.189.89.239/admin/statics/css/fontawesome.min.css

echo ""
echo "🎉 Admin CSS fix completed!"
echo ""
echo "📖 Summary:"
echo "  - nginx now properly routes /admin/statics/ to FastAPI backend"
echo "  - Admin interface CSS should now load correctly"
echo "  - Static files are cached for 1 day for better performance"
echo ""
echo "🌐 Access your admin interface at: http://206.189.89.239/admin/"