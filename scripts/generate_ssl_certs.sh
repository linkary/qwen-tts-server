#!/bin/bash

# Generate self-signed SSL certificates for development
# Usage: ./scripts/generate_ssl_certs.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CERTS_DIR="$PROJECT_DIR/certs"

# Create certs directory if it doesn't exist
mkdir -p "$CERTS_DIR"

# Certificate configuration
DAYS=365
COUNTRY="CN"
STATE="Local"
CITY="Development"
ORG="Qwen3-TTS Dev"
CN="localhost"

echo "🔐 Generating self-signed SSL certificates for development..."

# Generate private key and self-signed certificate
openssl req -x509 -nodes -days $DAYS -newkey rsa:2048 \
    -keyout "$CERTS_DIR/key.pem" \
    -out "$CERTS_DIR/cert.pem" \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/CN=$CN" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:$(hostname -I | awk '{print $1}')"

# Set permissions
chmod 600 "$CERTS_DIR/key.pem"
chmod 644 "$CERTS_DIR/cert.pem"

echo ""
echo "✅ SSL certificates generated successfully!"
echo ""
echo "📁 Certificate: $CERTS_DIR/cert.pem"
echo "🔑 Private Key: $CERTS_DIR/key.pem"
echo ""
echo "To enable HTTPS, add these to your .env file:"
echo ""
echo "    SSL_ENABLED=true"
echo "    SSL_CERTFILE=$CERTS_DIR/cert.pem"
echo "    SSL_KEYFILE=$CERTS_DIR/key.pem"
echo ""
echo "⚠️  Note: Browsers will show a security warning for self-signed certificates."
echo "    Click 'Advanced' → 'Proceed to localhost' to continue."
