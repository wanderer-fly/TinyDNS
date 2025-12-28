import threading
import time
import uvicorn
from dns.server import start_dns
from db.models import init_db
from web.api import app

if __name__ == '__main__':
    init_db()
    
    threading.Thread(target=start_dns ,daemon=True).start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)