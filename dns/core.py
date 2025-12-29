from dnslib import DNSRecord
from dns.resolver import resolve_query
from dns.context import DNSContext

def handle_dns(raw: bytes, ctx: DNSContext) -> bytes:
    dns_request = DNSRecord.parse(raw)
    dns_reply = resolve_query(dns_request, ctx)
    return bytes(dns_reply.pack())