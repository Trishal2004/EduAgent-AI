import requests
import sys

response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    data={
        'grant_type': '',
        'username': 'testuser@example.com',
        'password': 'password',
        'scope': '',
        'client_id': '',
        'client_secret': ''
    },
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
if response.status_code != 200:
    print(f"Login Failed: {response.text}")
    sys.exit(1)

token = response.json()['access_token']

# Get Document ID
docs = requests.get('http://localhost:8000/api/v1/documents', headers={'Authorization': f'Bearer {token}'})
doc_id = None
if docs.status_code == 200 and len(docs.json()) > 0:
    doc_id = docs.json()[0]['id']

print(f"Using Document ID: {doc_id}")

res = requests.post(
    'http://localhost:8000/api/v1/srs/decks/generate',
    headers={'Authorization': f'Bearer {token}'},
    json={
        "topic": "Document Deck",
        "card_type": "definition",
        "number_of_cards": 10,
        "difficulty": "medium",
        "document_id": doc_id
    }
)
print(f"Status: {res.status_code}")
print(f"Response: {res.text}")
