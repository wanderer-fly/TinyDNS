from dataclasses import dataclass

@dataclass(frozen=True)
class DNSContext:
    client_ip: str
    client_port: int
    protocol: str          # udp / tcp / doh
    server_ip: str | None = None
    is_https: bool = False
    user_agent: str | None = None
    
    def __str__(self):
        return f"{self.protocol} {self.client_ip}:{self.client_port}"
