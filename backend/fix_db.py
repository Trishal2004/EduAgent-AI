import sqlite3

conn = sqlite3.connect('eduagent.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE srs_cards RENAME COLUMN front TO question;')
    cursor.execute('ALTER TABLE srs_cards RENAME COLUMN back TO answer;')
    cursor.execute('ALTER TABLE srs_cards ADD COLUMN difficulty VARCHAR(50) DEFAULT "medium";')
    cursor.execute('ALTER TABLE srs_cards ADD COLUMN status VARCHAR(50) DEFAULT "new";')
    conn.commit()
    print("Successfully migrated srs_cards.")
except Exception as e:
    print(f"Error altering table: {e}")

conn.close()
