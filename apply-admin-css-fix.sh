#!/bin/bash

echo "🔧 Admin CSS Fix - Application Instructions"
echo "==========================================="
echo ""
echo "⚠️  NOTICE: This script requires Docker access on the production server"
echo "    The nginx configuration has been updated but needs to be applied."
echo ""

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not available in this environment"
    echo ""
    echo "📋 MANUAL APPLICATION REQUIRED:"
    echo "   Please run the following commands on the production server:"
    echo ""
    echo "   1. Navigate to the project directory"
    echo "   2. Run one of these commands:"
    echo ""
    echo "      # Option 1: Quick rebuild and restart"
    echo "      docker-compose -f docker-compose.prod.yml build nginx && docker-compose -f docker-compose.prod.yml restart nginx"
    echo ""
    echo "      # Option 2: Use existing script"
    echo "      ./rebuild_nginx.sh"
    echo ""
    echo "      # Option 3: Full restart (if other options fail)"
    echo "      docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d"
    echo ""
    echo "   3. Test the fix:"
    echo "      curl -I http://206.189.89.239/admin/statics/css/tabler.min.css"
    echo ""
    echo "✅ Expected result: HTTP/1.1 200 OK (instead of 404)"
    echo ""
    exit 1
fi

echo "🚀 Docker is available, proceeding with fix application..."
echo ""

# Check if production compose file exists
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ docker-compose.prod.yml not found in current directory"
    echo "   Please run this script from the project root directory"
    exit 1
fi

echo "📁 Found docker-compose.prod.yml"
echo ""

# Show what will be done
echo "📋 Fix Summary:"
echo "  - Problem: Admin CSS files return 404 (routed to Next.js instead of FastAPI)"
echo "  - Solution: Added /admin/statics/ location block in nginx config"
echo "  - Files updated: nginx/nginx.prod.conf, nginx/default.conf"
echo ""

# Confirm before proceeding
read -p "🤔 Do you want to apply the fix by rebuilding nginx? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Fix application cancelled"
    exit 1
fi

echo ""
echo "🔨 Rebuilding nginx container with updated configuration..."
docker-compose -f docker-compose.prod.yml build nginx

if [ $? -eq 0 ]; then
    echo "✅ Nginx rebuilt successfully"
else
    echo "❌ Failed to rebuild nginx"
    exit 1
fi

echo ""
echo "🔄 Restarting nginx container..."
docker-compose -f docker-compose.prod.yml restart nginx

if [ $? -eq 0 ]; then
    echo "✅ Nginx restarted successfully"
else
    echo "❌ Failed to restart nginx"
    exit 1
fi

echo ""
echo "⏳ Waiting for nginx to be ready..."
sleep 10

echo ""
echo "🧪 Testing the fix..."

# Test admin page
echo "Testing admin page..."
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://206.189.89.239/admin/)
echo "  Admin page: $ADMIN_STATUS"

# Test CSS files
echo "Testing CSS files..."
CSS1_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://206.189.89.239/admin/statics/css/tabler.min.css)
echo "  tabler.min.css: $CSS1_STATUS"

CSS2_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://206.189.89.239/admin/statics/css/main.css)
echo "  main.css: $CSS2_STATUS"

CSS3_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://206.189.89.239/admin/statics/css/fontawesome.min.css)
echo "  fontawesome.min.css: $CSS3_STATUS"

echo ""

# Check results
if [[ "$CSS1_STATUS" == "200" && "$CSS2_STATUS" == "200" && "$CSS3_STATUS" == "200" ]]; then
    echo "🎉 SUCCESS! Admin CSS fix has been applied successfully!"
    echo ""
    echo "✅ All CSS files are now returning HTTP 200"
    echo "✅ Admin interface should display with proper styling"
    echo "✅ Static files are cached for improved performance"
    echo ""
    echo "🌐 Access your admin interface at: http://206.189.89.239/admin/"
else
    echo "⚠️  WARNING: Some CSS files are still returning errors"
    echo ""
    echo "🔍 Troubleshooting steps:"
    echo "  1. Check nginx logs: docker-compose -f docker-compose.prod.yml logs nginx"
    echo "  2. Verify nginx config: docker exec pm_nginx nginx -t"
    echo "  3. Check FastAPI logs: docker-compose -f docker-compose.prod.yml logs fastapi"
    echo ""
    echo "📧 If issues persist, contact the development team with the above output"
fi

echo ""
echo "📝 For more details, see: ADMIN_CSS_FIX.md"