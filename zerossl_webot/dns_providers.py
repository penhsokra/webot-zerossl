class DNSProvider:
    def add_txt_record(self, domain, value):
        raise NotImplementedError

class ManualDNS(DNSProvider):
    def add_txt_record(self, domain, value):
        print(f"Add TXT record for {domain}: {value}")
        input("Press Enter after DNS propagation...")

class CloudflareDNS(DNSProvider):
    def __init__(self, api_token):
        self.api_token = api_token

    def add_txt_record(self, domain, value):
        import requests
        print(f"[Cloudflare] Add TXT record for {domain}: {value}")
        # Real implementation: call Cloudflare API to add TXT record