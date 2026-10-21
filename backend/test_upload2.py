from app.security.security import create_access_token
import requests

token = create_access_token(data={"sub": "1"})
url = "http://localhost:8000/api/v1/documents/upload"
headers = {"Authorization": f"Bearer {token}"}
files = {'file': ('test.pdf', open('test.pdf', 'rb'), 'application/pdf')}

response = requests.post(url, headers=headers, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
