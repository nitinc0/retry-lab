import sqlite3

def initialize_database():
    # opens a connection to the DB. If file doesnt exist SQLite creates it 
    conn = sqlite3.connect("charges.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS charges (
            idempotency_key TEXT PRIMARY KEY,
            charge_id TEXT UNIQUE NOT NULL,
            order_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized!")
