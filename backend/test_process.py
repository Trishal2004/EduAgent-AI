from app.security.security import create_access_token
import requests

token = create_access_token(data={"sub": "1"})
url = "http://localhost:8000/api/v1/documents/b472db4a-b844-4ab7-9437-339845493373/process"
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
