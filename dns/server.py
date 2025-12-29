from dnslib.server import DNSServer, BaseResolver
from dns.resolver import resolve_query
from dns.context import DNSContext

class Resolver(BaseResolver):
    def resolve(self, request, handler):
        client_ip, client_port = handler.client_address
        ctx = DNSContext(
            client_ip=client_ip,
            client_port=client_port,
            protocol=handler.protocol
        )
        return resolve_query(request, ctx)
    
def start_dns():
    server = DNSServer(
        Resolver(),
        port=53,
        address="0.0.0.0",
        tcp=False
    )
    server.start_thread()