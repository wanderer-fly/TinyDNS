from db.database import get_db

def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS dns_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        value TEXT NOT NULL,
        ttl INTEGER DEFAULT 60
    )
    """)
    db.commit()
    
def get_records(name):
    db = get_db()
    cursor = db.execute("SELECT * FROM dns_records WHERE name = ?", (name,))
    return cursor.fetchall()

def add_record(name, rtype, value, ttl=60):
    db = get_db()
    db.execute("INSERT INTO dns_records (name, type, value, ttl) VALUES (?, ?, ?, ?)",
               (name, rtype, value, ttl))
    db.commit()