import requests
import json
import sys

# Login
login_res = requests.post(
    'http://localhost:8000/api/v1/auth/login', 
    data={'grant_type': 'password', 'username': 'testuser@example.com', 'password': 'password'},
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
if login_res.status_code != 200:
    print(f"Login failed: {login_res.text}")
    sys.exit(1)

token = login_res.json()['access_token']
print("Login successful.")

# Generate Flashcards
res = requests.post(
    'http://localhost:8000/api/v1/srs/decks/generate',
    headers={'Authorization': f'Bearer {token}'},
    json={
        "topic": "Laser and Optical Fibers",
        "card_type": "definition",
        "number_of_cards": 10,
        "difficulty": "medium",
        # omitting document_id for now to test general knowledge fallback
    }
)
print(f"Status: {res.status_code}")
print(res.text)
