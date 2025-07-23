#!/bin/bash

# Generate self-signed SSL certificate for development
# For production, use proper certificates from a CA

echo "Generating self-signed SSL certificate for development..."

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate private key
openssl genrsa -out ssl/key.pem 2048

# Generate certificate signing request
openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem

# Set proper permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

# Clean up CSR file
rm ssl/cert.csr

echo "SSL certificate generated successfully!"
echo "Files created:"
echo "  - ssl/key.pem (private key)"
echo "  - ssl/cert.pem (certificate)"
echo ""
echo "Note: This is a self-signed certificate for development only."
echo "For production, use certificates from a trusted Certificate Authority." 