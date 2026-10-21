import asyncio
import os
import requests
from pydantic_settings import BaseSettings

# We need to generate a valid token
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

# Let's create a token for user 1
expire = datetime.utcnow() + timedelta(minutes=60)
to_encode = {"sub": "1", "exp": expire}
token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

print(f"Token: {token}")

# Create a mock PDF file
with open("test.pdf", "wb") as f:
    f.write(b"%PDF-1.4\n%EOF")

url = "http://localhost:8000/api/v1/documents/upload"
headers = {"Authorization": f"Bearer {token}"}
files = {'file': ('test.pdf', open('test.pdf', 'rb'), 'application/pdf')}

response = requests.post(url, headers=headers, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
