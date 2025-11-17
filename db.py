import sqlite3
import json
from typing import List, Dict, Optional

DB_FILE = "leads.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        score INTEGER DEFAULT 0,
        stage TEXT DEFAULT 'new',
        notes TEXT,
        interactions TEXT DEFAULT '[]'
    )
""")
    conn.commit()
    conn.close()

def create_lead(lead_data: Dict) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (name, company, email, notes) VALUES (?, ?, ?, ?)
    """, (lead_data['name'], lead_data['company'], lead_data['email'], lead_data.get('notes', '')))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lead_id

def read_lead(lead_id: int) -> Optional[Dict]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0], 'name': row[1], 'company': row[2], 'email': row[3],
            'score': row[4], 'stage': row[5], 'notes': row[6],
            'interactions': json.loads(row[7]) if row[7] else []
        }
    return None

def update_lead_score(lead_id: int, score: int, criteria: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET score = ? WHERE id = ?", (score, lead_id))
    # Log interaction
    interactions = json.loads((read_lead(lead_id) or {}).get('interactions', '[]'))
    interactions.append({"date": "2025-11-16", "type": "score_update", "content": f"Scored {score} based on: {criteria}"})
    cursor.execute("UPDATE leads SET interactions = ? WHERE id = ?", (json.dumps(interactions), lead_id))
    conn.commit()
    conn.close()

def search_leads(query: str) -> List[Dict]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE name LIKE ? OR company LIKE ? OR email LIKE ?", (f"%{query}%", f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "company": r[2], "email": r[3], "score": r[4], "stage": r[5]} for r in rows]

# Init on import
init_db()