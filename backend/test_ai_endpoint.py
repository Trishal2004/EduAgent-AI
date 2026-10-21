import asyncio
import httpx
import uuid
import pymysql

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def get_auth_token():
    email = f"test_ai_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPassword123!"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Register
        await client.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "password_confirm": password
        })
        
        # Get OTP from DB
        conn = pymysql.connect(host='127.0.0.1', user='root', database='eduagent')
        cursor = conn.cursor()
        cursor.execute("SELECT verification_otp FROM users WHERE email = %s", (email,))
        otp = cursor.fetchone()[0]
        conn.close()

        # Verify email
        await client.post(f"{BASE_URL}/auth/verify-email", json={
            "email": email,
            "otp": otp
        })

        # Login
        login_resp = await client.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        return login_resp.json()["access_token"]

async def test_ai_endpoint():
    print("=== Getting Auth Token ===")
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    questions = [
        "What is machine learning?",
        "Explain binary search with Python.",
        "What is normalization in DBMS?",
        "Explain recursion.",
        "Can you give another example of recursion?" # Follow-up
    ]
    
    async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
        # Create a session
        resp = await client.post(f"{BASE_URL}/tutor/session")
        session_id = resp.json()["id"]
        
        for q in questions:
            print(f"\n=== Testing Question: {q} ===")
            resp = await client.post(f"{BASE_URL}/tutor/chat", json={
                "session_id": session_id,
                "question": q,
                "document_id": None
            })
            
            if resp.status_code == 200:
                print("Success! AI Response received.")
                print("Content preview:", str(resp.json().get("ai_message", {}).get("structured_data", {}))[:100])
            else:
                print(f"Failed with {resp.status_code}: {resp.json()}")

if __name__ == "__main__":
    asyncio.run(test_ai_endpoint())
