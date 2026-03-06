# ZeroSSL Webot

Automate ZeroSSL certificate issuance and renewal using the ACME protocol and DNS validation.

## Features

- **Automatic Renewal**: Checks local certificate expiration and renews automatically if within the threshold.
- **DNS Validation**: Supports both Manual and Cloudflare DNS providers.
- **Nginx Integration**: Automatically reloads Nginx after certificate installation.
- **Non-Interactive**: Designed for cron jobs and automated environments.
- **Robustness**: Uses `subprocess` with error handling and logging.

## Installation

### Prerequisites

- Python 3.6+
- `pip install requests`
- `zerossl-bot` (ACME client) installed and in your PATH.
- `openssl` for certificate checking.

### Quick Install

Use the provided `install.sh` script to set up the environment and configuration:

```bash
chmod +x install.sh
sudo ./install.sh
```

This script will:
1. Install the bot to `/usr/local/webot-zerossl`.
2. Create a symlink `webot-zerossl` in `/usr/local/bin`.
3. Prompt you for configuration details (domains, ZeroSSL EAB credentials, etc.).
4. Create a default configuration at `/etc/webot-zerossl/config.json`.

## Configuration

The configuration is stored in `config.json`. Example structure:

```json
{
  "domains": ["example.com", "www.example.com"],
  "email": "admin@example.com",
  "cert_dir": "/etc/nginx/ssl",
  "nginx_reload_cmd": "systemctl reload nginx",
  "eab_kid": "YOUR_EAB_KID",
  "eab_hmac": "YOUR_EAB_HMAC",
  "renew_before_days": 7,
  "log_file": "/var/log/webot-zerossl.log",
  "dns_provider": "cloudflare",
  "dns_api_token": "YOUR_CLOUDFLARE_TOKEN"
}
```

### DNS Providers

- `manual`: The bot will prompt you to add TXT records manually (not recommended for automated cron jobs).
- `cloudflare`: Uses the Cloudflare API to automatically add and remove `_acme-challenge` TXT records.

## Usage

Run the bot manually:

```bash
webot-zerossl
```

Or specify a custom configuration file:

```bash
webot-zerossl --config /path/to/your/config.json
```

### Automating with Cron

To automate renewal, add a cron job (running as root or a user with necessary permissions):

```bash
0 0 * * * /usr/local/bin/webot-zerossl >> /var/log/webot-zerossl-cron.log 2>&1
```

## Troubleshooting

- **Logs**: Check the log file specified in your `config.json` (default: `/var/log/webot-zerossl.log`).
- **Nginx**: Ensure the user running the bot has permissions to execute the `nginx_reload_cmd`.
- **Certificates**: Certificates are typically issued to `/etc/letsencrypt/live/<domain>/` by `zerossl-bot` before being copied to your `cert_dir`.
