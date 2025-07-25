#!/bin/bash

# Fix permissions for Next.js development
echo "Fixing permissions for Next.js development..."

# Create next-env.d.ts if it doesn't exist
if [ ! -f "frontend/next-env.d.ts" ]; then
    echo "Creating next-env.d.ts..."
    touch frontend/next-env.d.ts
fi

# Set proper permissions for the frontend directory
# Make sure the files are readable/writable by user and group
find frontend -type f -exec chmod 664 {} \;
find frontend -type d -exec chmod 775 {} \;

# Specifically handle next-env.d.ts
chmod 664 frontend/next-env.d.ts

# Create .next directory if it doesn't exist
mkdir -p frontend/.next
chmod 775 frontend/.next

echo "Permissions fixed successfully!"
echo "You can now run: docker-compose up --build"