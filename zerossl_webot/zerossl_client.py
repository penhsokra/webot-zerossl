import subprocess
import logging

class ZeroSSLClient:
    def __init__(self, config):
        self.config = config
        self.eab_kid = config["eab_kid"]
        self.eab_hmac = config["eab_hmac"]
        self.logger = logging.getLogger(__name__)

    def obtain_certificate(self, domains, dns_provider):
        cmd = [
            "zerossl-bot", "certonly",
            "--server", "https://acme.zerossl.com/v2/DV90",
            "--eab-kid", self.eab_kid,
            "--eab-hmac-key", self.eab_hmac,
            "--email", self.config['email'],
            "--non-interactive", "--agree-tos"
        ]
        for d in domains:
            cmd.extend(["-d", d])

        if dns_provider:
            if dns_provider.lower() == "manual":
                cmd.extend(["--manual", "--preferred-challenges", "dns"])
            else:
                cmd.extend([f"--dns-{dns_provider}", f"--dns-{dns_provider}-credentials", self.config['dns_api_token']])
        
        self.logger.info(f"Running command: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("Certificate obtained successfully.")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error obtaining certificate: {e.stderr}")
            raise