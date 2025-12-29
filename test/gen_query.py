from dnslib import DNSRecord

q = DNSRecord.question("test.mydns", "A")
open("query.bin", "wb").write(q.pack())

str = """
curl -H 'Content-Type: application/dns-message' --data-binary @query.bin https://localhost:8000/dns-query
"""

print(f"Usage: \n{str}")