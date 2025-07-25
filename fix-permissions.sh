#!/bin/bash

# Fix permissions for Next.js development
echo "Fixing permissions for Next.js development..."

# Get current user info
USER_UID=$(id -u)
USER_GID=$(id -g)
echo "Current user UID: $USER_UID, GID: $USER_GID"

# Create next-env.d.ts if it doesn't exist
if [ ! -f "frontend/next-env.d.ts" ]; then
    echo "Creating next-env.d.ts..."
    touch frontend/next-env.d.ts
fi

# Set ownership to current user
chown -R $USER_UID:$USER_GID frontend/ 2>/dev/null || sudo chown -R $USER_UID:$USER_GID frontend/

# Set proper permissions for the frontend directory
# Use 777 for maximum compatibility with Docker volumes
find frontend -type f -exec chmod 666 {} \;
find frontend -type d -exec chmod 777 {} \;

# Specifically handle next-env.d.ts
chmod 666 frontend/next-env.d.ts

# Create .next directory if it doesn't exist
mkdir -p frontend/.next
chmod 777 frontend/.next

# Make scripts executable
chmod +x *.sh 2>/dev/null || true

echo "Permissions fixed successfully!"
echo "UID: $USER_UID, GID: $USER_GID"
echo "You can now run: ./restart-dev.sh"