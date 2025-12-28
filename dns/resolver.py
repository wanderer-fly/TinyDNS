from dnslib import DNSRecord, QTYPE, RR, A
from db.models import get_records
import socket

UPSTREAM_DNS = ("8.8.8.8", 53) # 上游DNS

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
    
    # 转发给上游DNS
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(request.pack(), UPSTREAM_DNS)
    response, _ = sock.recvfrom(512)
    sock.close()

    reply = DNSRecord.parse(response)

