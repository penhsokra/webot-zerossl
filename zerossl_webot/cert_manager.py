import os
import subprocess
from datetime import datetime, timedelta
from .zerossl_client import ZeroSSLClient

class CertManager:
    def __init__(self, config, dns_provider=None):
        self.config = config
        self.cert_path = os.path.join(config["cert_dir"], "fullchain.pem")
        self.key_path = os.path.join(config["cert_dir"], "privkey.pem")
        self.renew_before = timedelta(days=config.get("renew_before_days", 7))
        self.dns_provider = dns_provider
        self.client = ZeroSSLClient(config)

    def log(self, msg):
        print(f"{datetime.now()} - {msg}")
        os.makedirs(os.path.dirname(self.config["log_file"]), exist_ok=True)
        with open(self.config["log_file"], "a") as f:
            f.write(f"{datetime.now()} - {msg}\n")

    def cert_needs_renewal(self):
        if not os.path.exists(self.cert_path):
            self.log("Certificate not found, will issue new one.")
            return True
        output = subprocess.check_output(
            ["openssl", "x509", "-enddate", "-noout", "-in", self.cert_path]
        ).decode().strip()
        expire_str = output.split("=")[1]
        expire_date = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z")
        if expire_date - datetime.utcnow() <= self.renew_before:
            self.log(f"Certificate expires soon: {expire_date}")
            return True
        self.log(f"Certificate valid until {expire_date}")
        return False

    def issue_certificate(self):
        self.log("Issuing/renewing certificate...")
        self.client.obtain_certificate(self.config["domains"], self.dns_provider)
        self.log("Certificate issuance finished.")

    def install_certificate(self, issued_cert, issued_key):
        os.makedirs(self.config["cert_dir"], exist_ok=True)
        subprocess.run(f"cp {issued_cert} {self.cert_path}", shell=True)
        subprocess.run(f"cp {issued_key} {self.key_path}", shell=True)
        self.log("Certificates installed")
        subprocess.run(self.config["nginx_reload_cmd"], shell=True)
        self.log("Nginx reloaded successfully")