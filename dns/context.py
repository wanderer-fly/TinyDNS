from dataclasses import dataclass

@dataclass
class DNSContext:
    client_ip: str
    client_port: int
    protocol: str
