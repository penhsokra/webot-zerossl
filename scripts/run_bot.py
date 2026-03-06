#!/usr/bin/env python3
import json
from zerossl_webot.cert_manager import CertManager
from zerossl_webot.dns_providers import ManualDNS, CloudflareDNS

CONFIG_PATH = "/etc/zerossl-webot/config.json"
with open(CONFIG_PATH) as f:
    config = json.load(f)

provider = config.get("dns_provider", "manual").lower()
dns = None
if provider == "manual":
    dns = ManualDNS()
elif provider == "cloudflare":
    dns = CloudflareDNS(config.get("dns_api_token"))

bot = CertManager(config, dns_provider=provider)

if bot.cert_needs_renewal():
    bot.issue_certificate()
    issued_cert = input("Path to fullchain.pem: ").strip()
    issued_key = input("Path to privkey.pem: ").strip()
    bot.install_certificate(issued_cert, issued_key)
else:
    bot.log("No renewal needed.")