import sqlite3
from datetime import datetime

db = sqlite3.connect("database.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    client_name TEXT,
    username TEXT,
    telegram_id TEXT,
    brand TEXT,
    model TEXT,
    year TEXT,
    budget TEXT,
    source_country TEXT,
    delivery_city TEXT,
    phone TEXT,
    comment TEXT,
    status TEXT
)
""")

db.commit()


def create_lead(
    client_name,
    username,
    telegram_id,
    brand,
    model,
    year,
    budget,
    source_country,
    delivery_city,
    phone,
    comment
):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO leads (
        created_at,
        client_name,
        username,
        telegram_id,
        brand,
        model,
        year,
        budget,
        source_country,
        delivery_city,
        phone,
        comment,
        status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        created_at,
        client_name,
        username,
        telegram_id,
        brand,
        model,
        year,
        budget,
        source_country,
        delivery_city,
        phone,
        comment,
        "new"
    ))

    db.commit()

    return cursor.lastrowid


def get_last_leads(limit=10):
    cursor.execute("""
    SELECT
        id,
        created_at,
        brand,
        model,
        budget,
        source_country,
        delivery_city,
        phone,
        status
    FROM leads
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    return cursor.fetchall()

def get_new_leads(limit=10):
    cursor.execute("""
    SELECT
        id,
        created_at,
        client_name,
        brand,
        model,
        budget,
        source_country,
        delivery_city,
        phone,
        status
    FROM leads
    WHERE status = 'new'
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    return cursor.fetchall()


def get_stats():
    cursor.execute("SELECT COUNT(*) FROM leads")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'new'")
    new = cursor.fetchone()[0]

    return {
        "total": total,
        "new": new
    }
def update_lead_status(lead_id, status):
    cursor.execute("""
    UPDATE leads
    SET status = ?
    WHERE id = ?
    """, (status, lead_id))

    db.commit()

    return cursor.rowcount

def get_lead_by_id(lead_id):
    cursor.execute("""
    SELECT
        id,
        created_at,
        client_name,
        username,
        telegram_id,
        brand,
        model,
        year,
        budget,
        source_country,
        delivery_city,
        phone,
        comment,
        status
    FROM leads
    WHERE id = ?
    """, (lead_id,))

    return cursor.fetchone()

def get_all_leads():
    cursor.execute("""
    SELECT
        id,
        created_at,
        client_name,
        username,
        telegram_id,
        brand,
        model,
        year,
        budget,
        source_country,
        delivery_city,
        phone,
        comment,
        status
    FROM leads
    ORDER BY id DESC
    """)

    return cursor.fetchall()