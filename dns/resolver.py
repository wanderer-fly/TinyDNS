from dnslib import DNSRecord, QTYPE, RR, A
from db.models import get_records
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
    qname = str(request.q.qname).rstrip(".")
    qtype = QTYPE[request.q.qtype]
    
    print(f"[DNS] {ctx.client_ip}:{ctx.client_port} ({ctx.protocol}) -> {qname} ({qtype})")

    records = get_records(qname)
    if (records):
        reply = request.reply()
        for r in records:
            if (r["type"] == qtype):
                reply.add_answer(
                    RR(
                        qname,
                        QTYPE.A,
                        rdata=A(r["value"]),
                        ttl=r["ttl"]
                    )
                )
        return reply
    return forward_to_upstream(request)

