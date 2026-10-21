from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document
db = SessionLocal()
doc = db.query(Document).first()
print(doc.id)
