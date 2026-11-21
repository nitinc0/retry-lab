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

def insert_charge(idempotency_key, charge_id, order_id, amount, status):
    conn = sqlite3.connect("charges.db")

    try:
        conn.execute("""
            INSERT INTO charges
            (idempotency_key, charge_id, order_id, amount, status)
            VALUES(?, ?, ?, ?, ?)
        """, (idempotency_key, charge_id, order_id, amount, status))

        conn.commit()
    finally: # regardless of failure etc. we always close this resource out (resource management)
        conn.close()



def get_charge(idempotency_key):
    conn = sqlite3.connect("charges.db")
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute("""
            SELECT * FROM charges
            WHERE idempotency_key = ?
        """, (idempotency_key,))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)
    finally:
        conn.close()

def get_charge_by_id(charge_id):
    conn = sqlite3.connect("charges.db")
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute("""
            SELECT * FROM charges
            WHERE charge_id = ?
        """, (charge_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)
    finally:
        conn.close()





if __name__ == "__main__":
    initialize_database()
    print("Database initialized!")

    # Only insert if the demo charge doesn't exist
    if get_charge("test_key") is None:
        insert_charge(
            "test_key",
            "ch_001",
            "order_123",
            500,
            "success"
        )

    result = get_charge("test_key")
    print(result)