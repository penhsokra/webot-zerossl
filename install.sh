#!/bin/bash
set -e

INSTALL_DIR="/usr/local/webot-zerossl"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="/etc/webot-zerossl"

echo "Installing Webot ZeroSSL to $INSTALL_DIR..."

TMP_FILE="/tmp/webot-zerossl-1.0.0.tar.gz"
curl -L -o "$TMP_FILE" "https://penhsokra.com/webot-zerossl-1.0.0.tar.gz"

mkdir -p "$INSTALL_DIR"
tar -xzf "$TMP_FILE" -C "$INSTALL_DIR" --strip-components=1
chmod +x "$INSTALL_DIR/scripts/run_bot.py"
ln -sf "$INSTALL_DIR/scripts/run_bot.py" "$BIN_DIR/webot-zerossl"

mkdir -p "$CONFIG_DIR"

echo "=== Configure Webot ZeroSSL ==="
read -p "Enter your domains (comma-separated): " DOMAINS
read -p "Enter your email: " EMAIL
read -p "Enter your ZeroSSL EAB KID: " EAB_KID
read -p "Enter your ZeroSSL EAB HMAC Key: " EAB_HMAC
read -p "Enter your cert directory [/etc/nginx/ssl]: " CERT_DIR
CERT_DIR=${CERT_DIR:-/etc/nginx/ssl}

echo "Select DNS provider:"
echo "1) Manual DNS"
echo "2) Cloudflare"
read -p "Choose [1-2]: " DNS_CHOICE
if [ "$DNS_CHOICE" == "2" ]; then
    read -p "Enter Cloudflare API token: " CF_TOKEN
    DNS_PROVIDER="cloudflare"
else
    DNS_PROVIDER="manual"
    CF_TOKEN=""
fi

DOMAINS_JSON=$(echo $DOMAINS | sed 's/ *, */,/g' | sed 's/[^,]*/"&"/g' | sed 's/,/, /g')

cat > "$CONFIG_DIR/config.json" <<EOL
{
  "domains": [${DOMAINS_JSON}],
  "email": "${EMAIL}",
  "cert_dir": "${CERT_DIR}",
  "nginx_reload_cmd": "systemctl reload nginx",
  "eab_kid": "${EAB_KID}",
  "eab_hmac": "${EAB_HMAC}",
  "renew_before_days": 7,
  "log_file": "/var/log/webot-zerossl.log",
  "dns_provider": "${DNS_PROVIDER}",
  "dns_api_token": "${CF_TOKEN}",
  "dns_credentials_path": ""
}
EOL

echo "Installation complete! Run the bot with: webot-zerossl"