import threading
import time
import uvicorn
from dns.server import start_dns
from db.models import init_db
from api import app
import dns.doh

if __name__ == '__main__':
    init_db()
    
    threading.Thread(target=start_dns ,daemon=True).start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_certfile='./ssl/localhost+3.pem', ssl_keyfile='./ssl/localhost+3-key.pem')