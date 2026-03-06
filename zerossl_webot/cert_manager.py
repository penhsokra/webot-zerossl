import os
import subprocess
import shutil
import logging
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
        self.logger = logging.getLogger(__name__)

    def cert_needs_renewal(self):
        if not os.path.exists(self.cert_path):
            self.logger.info("Certificate not found, will issue new one.")
            return True
        try:
            output = subprocess.check_output(
                ["openssl", "x509", "-enddate", "-noout", "-in", self.cert_path],
                stderr=subprocess.STDOUT
            ).decode().strip()
            expire_str = output.split("=")[1]
            expire_date = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z")
            if expire_date - datetime.utcnow() <= self.renew_before:
                self.logger.info(f"Certificate expires soon: {expire_date}")
                return True
            self.logger.info(f"Certificate valid until {expire_date}")
            return False
        except (subprocess.CalledProcessError, IndexError, ValueError) as e:
            self.logger.error(f"Error checking certificate status: {e}")
            return True

    def issue_certificate(self):
        self.logger.info("Issuing/renewing certificate...")
        try:
            self.client.obtain_certificate(self.config["domains"], self.dns_provider)
            self.logger.info("Certificate issuance finished.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to issue certificate: {e}")
            return False

    def install_certificate(self, issued_cert, issued_key):
        try:
            os.makedirs(self.config["cert_dir"], exist_ok=True)
            shutil.copy2(issued_cert, self.cert_path)
            shutil.copy2(issued_key, self.key_path)
            self.logger.info(f"Certificates installed to {self.config['cert_dir']}")
            
            if "nginx_reload_cmd" in self.config:
                subprocess.run(self.config["nginx_reload_cmd"], shell=True, check=True)
                self.logger.info("Nginx reloaded successfully")
            return True
        except (shutil.Error, subprocess.CalledProcessError, OSError) as e:
            self.logger.error(f"Error installing certificate: {e}")
            return False
