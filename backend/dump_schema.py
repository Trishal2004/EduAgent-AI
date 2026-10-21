import sqlite3

conn = sqlite3.connect('eduagent.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(srs_decks);")
print("srs_decks:", cursor.fetchall())

cursor.execute("PRAGMA table_info(srs_cards);")
print("srs_cards:", cursor.fetchall())

conn.close()
