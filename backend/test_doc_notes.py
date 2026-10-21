from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.security.security import create_access_token
import requests
import json

db = SessionLocal()
user = db.query(User).first()
if user:
    doc = db.query(Document).filter(Document.owner_id == user.id).first()
    if doc:
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        data = {"topic": "Any", "note_type": "detailed", "document_id": str(doc.id)}
        print(f"Testing generate note with document {doc.id}...")
        res = requests.post("http://localhost:8000/api/v1/notes/generate", headers=headers, json=data)
        print(res.status_code)
        try:
            print(json.dumps(res.json(), indent=2)[:500])
        except:
            print(res.text)
    else:
        print("No documents found for user")
else:
    print("No user found")
