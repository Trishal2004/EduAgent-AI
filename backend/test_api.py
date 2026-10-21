from app.db.session import SessionLocal
from app.models.user import User
from app.security.security import create_access_token
import requests
import json
import sys
import logging

logging.basicConfig(level=logging.INFO)

try:
    db = SessionLocal()
    # Get the first user
    user = db.query(User).first()
    if not user:
        print("No users found in database.")
        sys.exit(1)
        
    print(f"Authenticated as User ID: {user.id} ({user.email})")
    
    # Create token
    access_token = create_access_token({"sub": str(user.id)})
    
    # Make request
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("http://localhost:8000/api/v1/notes", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2)[:1500] + "\n... (truncated if long)")
except Exception as e:
    print(f"Error: {e}")
