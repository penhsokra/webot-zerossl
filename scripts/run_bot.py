#!/usr/bin/env python3
import json
import argparse
import logging
import os
from zerossl_webot.cert_manager import CertManager
from zerossl_webot.dns_providers import ManualDNS, CloudflareDNS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zerossl-webot")

parser = argparse.ArgumentParser(description="ZeroSSL Bot Wrapper")
parser.add_argument("--config", default="/etc/zerossl-webot/config.json", help="Path to config file")
args = parser.parse_args()

if not os.path.exists(args.config):
    logger.error(f"Config file not found: {args.config}")
    exit(1)

with open(args.config) as f:
    config = json.load(f)

provider_name = config.get("dns_provider", "manual").lower()
dns = None
if provider_name == "manual":
    dns = ManualDNS()
elif provider_name == "cloudflare":
    dns = CloudflareDNS(config.get("dns_api_token"))

bot = CertManager(config, dns_provider=provider_name)

if bot.cert_needs_renewal():
    if bot.issue_certificate():
        # zerossl-bot typically saves to /etc/letsencrypt/live/<domain>/
        domain = config["domains"][0]
        issued_cert = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
        issued_key = f"/etc/letsencrypt/live/{domain}/privkey.pem"
        
        if os.path.exists(issued_cert) and os.path.exists(issued_key):
            bot.install_certificate(issued_cert, issued_key)
        else:
            logger.error(f"Could find issued certificates at {issued_cert} or {issued_key}")
else:
    logger.info("No renewal needed.")