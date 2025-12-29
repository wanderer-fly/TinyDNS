from dnslib import DNSRecord, QTYPE, RR, A
from db.models import get_records
from dns.cache import dns_cache
import socket

UPSTREAM_DNS = ("8.8.8.8", 53) # 上游DNS

def forward_to_upstream(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    try:
        sock.sendto(request.pack(), UPSTREAM_DNS)
        data, _ = sock.recvfrom(4096)
        reply = DNSRecord.parse(data)
        reply.header.ra = 1  # 标记 Recursion Available
        return reply

    except Exception as e:
        print("Upstream DNS error:", e)
        return request.reply()  # fallback，防止返回 None

    finally:
        sock.close()

def resolve_query(request: DNSRecord, ctx):
    qname = str(request.q.qname).lower()
    qtype_code = request.q.qtype
    qtype_name = QTYPE[qtype_code]

    print(f"[DNS] {ctx.client_ip}:{ctx.client_port} ({ctx.protocol}) -> {qname} ({qtype_name})")

    cache_key = (qname, qtype_code, request.q.qclass)

    # 查缓存
    cached = dns_cache.get(cache_key)
    if cached:
        print("[DNS] cache HIT")
        return DNSRecord.parse(cached)

    print("[DNS] cache MISS")

    records = get_records(qname)
    if records:
        reply = request.reply()
        min_ttl = None

        for r in records:
            if r["type"] == qtype_name:
                ttl = r.get("ttl", 60)
                min_ttl = ttl if min_ttl is None else min(min_ttl, ttl)
                reply.add_answer(
                    RR(
                        qname,
                        qtype_code,
                        rdata=A(r["value"]),
                        ttl=ttl
                    )
                )

        if reply.rr:
            dns_cache.set(cache_key, reply.pack(), min_ttl)
            return reply

    reply = forward_to_upstream(request)

    if reply.rr:
        ttl = min(rr.ttl for rr in reply.rr)
        dns_cache.set(cache_key, reply.pack(), ttl)

    return reply
