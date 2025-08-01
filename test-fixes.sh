#!/bin/bash

echo "🔍 Testing the fixes applied to resolve frontend errors..."
echo ""

echo "1. Environment Configuration Check:"
echo "   NEXTAUTH_URL: $(grep NEXTAUTH_URL .env)"
echo "   NEXT_PUBLIC_BACKEND_URL: $(grep NEXT_PUBLIC_BACKEND_URL .env)"
echo "   NODE_ENV: $(grep NODE_ENV .env)"
echo ""

echo "2. Docker Compose Configuration Check:"
echo "   Frontend env_file configuration:"
grep -A 5 "env_file:" docker-compose.yml || echo "   No env_file found"
echo ""

echo "3. Nginx Configuration Check:"
echo "   Health endpoint in default.conf:"
grep -A 5 "location /health" nginx/default.conf | head -6
echo ""

echo "   Checking for hardcoded health responses:"
if grep -r "return 200.*healthy" nginx/default.conf >/dev/null 2>&1; then
    echo "   ❌ Found hardcoded health response in default.conf"
else
    echo "   ✅ No hardcoded health response in default.conf"
fi

if grep -r "return 200.*healthy" nginx/nginx.prod.conf >/dev/null 2>&1; then
    echo "   ⚠️  Found hardcoded health response in nginx.prod.conf (should not be used in dev)"
else
    echo "   ✅ No hardcoded health response in nginx.prod.conf"
fi
echo ""

echo "4. Frontend Health Check Code:"
echo "   Checking if health check handles both JSON and text responses:"
if grep -q "text.trim() === 'healthy'" frontend/src/app/page.tsx; then
    echo "   ✅ Health check now handles plain text 'healthy' responses"
else
    echo "   ❌ Health check might not handle plain text responses"
fi
echo ""

echo "5. NextAuth Configuration:"
echo "   Checking redirect function has debugging:"
if grep -q "console.log.*NextAuth redirect called" frontend/src/app/api/auth/\[...nextauth\]/route.ts; then
    echo "   ✅ NextAuth redirect function has debugging enabled"
else
    echo "   ❌ NextAuth redirect function missing debugging"
fi
echo ""

echo "Summary of fixes applied:"
echo "✅ Updated .env file to use localhost instead of production IP"
echo "✅ Modified docker-compose.yml to use .env file"
echo "✅ Enhanced frontend health check to handle both JSON and text responses"
echo "✅ Added debugging to NextAuth redirect function"
echo "✅ Added cache-control headers to health check requests"
echo ""

echo "To test these fixes:"
echo "1. Rebuild containers: docker-compose down && docker-compose build && docker-compose up"
echo "2. Check browser console for health check debugging info"
echo "3. Monitor NextAuth logs for redirect debugging"
echo "4. Verify health endpoint returns proper JSON by testing directly"