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
        self.base_url = "https://api.cloudflare.com/client/v4"

    def add_txt_record(self, domain, value):
        import requests
        print(f"[Cloudflare] Adding TXT record for {domain}: {value}")
        
        # 1. Get Zone ID
        zone_name = ".".join(domain.split(".")[-2:])
        headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}
        res = requests.get(f"{self.base_url}/zones?name={zone_name}", headers=headers)
        res.raise_for_status()
        zone_id = res.json()["result"][0]["id"]
        
        # 2. Add TXT Record
        data = {
            "type": "TXT",
            "name": f"_acme-challenge.{domain}",
            "content": value,
            "ttl": 120
        }
        res = requests.post(f"{self.base_url}/zones/{zone_id}/dns_records", headers=headers, json=data)
        res.raise_for_status()
        print(f"[Cloudflare] TXT record added successfully.")