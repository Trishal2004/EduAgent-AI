from app.db.session import SessionLocal
from app.models.note import Note
import json

db = SessionLocal()
notes = db.query(Note).all()
print(f"Total Notes Found: {len(notes)}")
for note in notes:
    print(json.dumps({
        "id": note.id,
        "title": note.title,
        "topic": note.topic,
        "note_type": note.note_type,
        "owner_id": note.owner_id
    }, indent=2))
