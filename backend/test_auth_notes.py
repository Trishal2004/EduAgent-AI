from app.db.session import SessionLocal
from app.models.user import User
from app.security.security import create_access_token
import requests

db = SessionLocal()
user = db.query(User).first()
if user:
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    data = {"topic": "Deadlock", "note_type": "detailed"}
    print("Testing generate note...")
    res = requests.post("http://localhost:8000/api/v1/notes/generate", headers=headers, json=data)
    print(res.status_code)
    print(res.text)
else:
    print("No user found")
