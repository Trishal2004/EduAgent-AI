from app.security.security import create_access_token
import requests

# We need the user's ID. Let's check who owns document 0797af0075f74f27b83d040ac91af225
import sqlite3
conn = sqlite3.connect("eduagent.db")
c = conn.cursor()
c.execute("SELECT owner_id FROM documents WHERE id = '0797af0075f74f27b83d040ac91af225'")
row = c.fetchone()
owner_id = row[0] if row else 1

token = create_access_token(data={"sub": str(owner_id)})
url = "http://localhost:8000/api/v1/documents/0797af00-75f7-4f27-b83d-040ac91af225/process"
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
