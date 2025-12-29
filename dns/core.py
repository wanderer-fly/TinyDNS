from dnslib import DNSRecord
from dns.resolver import resolve_query
from dns.context import DNSContext
from dns.cache import DNSCache
import time

cache = DNSCache(max_size=2048)

def handle_dns(raw: bytes, ctx: DNSContext) -> bytes:
    dns_request = DNSRecord.parse(raw)
    
    q = dns_request.q
    qname = str(q.qname).rstrip(".")
    qtype = q.qtype
    
    cache_key = (qname, qtype)
    
    # 查缓存
    cached = cache.get(cache_key)
    if (cached):
        print(f"[CACHE HIT] {qname}")
        return cached
    
    # 缓存没有
    dns_reply = resolve_query(dns_request, ctx)
    packed = bytes(dns_reply.pack())
    
    ttl_list = [rr.ttl for rr in dns_reply.rr] # RFC 8484
    ttl = min(ttl_list) if ttl_list else 30
    
    cache.set(cache_key, packed, ttl)
    
    print(f"[CACHE MISS] {qname} ttl={ttl}")
    
    return packed