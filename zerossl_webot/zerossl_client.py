import os

class ZeroSSLClient:
    def __init__(self, config):
        self.config = config
        self.eab_kid = config["eab_kid"]
        self.eab_hmac = config["eab_hmac"]

    def obtain_certificate(self, domains, dns_provider):
        domain_args = " ".join(f"-d {d}" for d in domains)
        cmd = f"zerossl-bot certonly --server https://acme.zerossl.com/v2/DV90 " \
              f"{domain_args} --eab-kid {self.eab_kid} --eab-hmac-key {self.eab_hmac} " \
              f"--email {self.config['email']}"
        if dns_provider:
            if dns_provider.lower() == "manual":
                cmd += " --manual --preferred-challenges dns"
            else:
                cmd += f" --dns-{dns_provider} --dns-{dns_provider}-credentials {self.config['dns_api_token']}"
        print(f"Run command:\n{cmd}")
        os.system(cmd)