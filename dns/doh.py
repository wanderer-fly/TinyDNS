from fastapi import Request, Response, HTTPException
from dnslib import DNSRecord
from dns.resolver import resolve_query
from api import app
import base64

def base64url_decode(data: str) -> bytes:
    # RFC 4648 base64url → 标准 base64
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

@app.get("/dns-query")
async def dns_query_get(request: Request):
    if (request.query_params.get("dns")):
        try:
            data = base64url_decode(request.query_params["dns"])
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid base64url")
        if (len(data) <= 12):
            raise HTTPException(status_code=400, detail="Invalid DNS message")
        
        try:
            dns_request = DNSRecord.parse(data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Bad DNS message: {e}")
        
        class Ctx:
            client_ip = request.client.host
            client_port = request.client.port
            protocol = "https"
        
        dns_reply = resolve_query(dns_request, ctx=Ctx())
        return Response(
            content=bytes(dns_reply.pack()),
            media_type="application/dns-message"
        )
        
    else:
        raise HTTPException(status_code=400, detail="Missing dns parameter")

@app.post("/dns-query")
async def dns_query(request: Request):
    if (request.headers.get("content-type") != "application/dns-message"):
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    data = await request.body()
    
    if (len(data) <= 12):
        raise HTTPException(status_code=400, detail="Invalid DNS request")
    
    try:
        dns_request = DNSRecord.parse(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad DNS message: {e}")
    
    class Ctx:
        client_ip = request.client.host
        client_port = request.client.port
        protocol = "https"
        
    dns_reply = resolve_query(dns_request, Ctx())
    
    return Response(
        content=bytes(dns_reply.pack()),
        media_type="application/dns-message"
    )