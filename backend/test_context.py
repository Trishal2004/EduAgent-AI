import asyncio
import httpx
import uuid
import pymysql

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def get_auth_token():
    email = f"test_ctx_{uuid.uuid4().hex[:8]}@example.com"
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

async def test_flow():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
        print("\n=== Test 1: New conversation & Multiple messages ===")
        # Conversation A
        resp_a = await client.post(f"{BASE_URL}/tutor/session")
        session_a = resp_a.json()["id"]
        
        # Message 1
        await client.post(f"{BASE_URL}/tutor/chat", json={
            "session_id": session_a,
            "question": "What is machine learning?",
            "document_id": None
        })
        print("Message 1 sent (Conversation A).")
        
        # Message 2 (Follow-up)
        await client.post(f"{BASE_URL}/tutor/chat", json={
            "session_id": session_a,
            "question": "What are its types?",
            "document_id": None
        })
        print("Message 2 sent (Follow-up on A).")

        print("\n=== Test 2: Switching to a second conversation ===")
        # Conversation B
        resp_b = await client.post(f"{BASE_URL}/tutor/session")
        session_b = resp_b.json()["id"]
        
        await client.post(f"{BASE_URL}/tutor/chat", json={
            "session_id": session_b,
            "question": "Explain normalization.",
            "document_id": None
        })
        print("Message 1 sent (Conversation B).")
        
        print("\n=== Test 3: Loading an old conversation ===")
        # Fetch Conversation A to simulate "refresh" or loading
        hist_a = await client.get(f"{BASE_URL}/tutor/session/{session_a}")
        messages = hist_a.json()["messages"]
        print(f"Loaded Conversation A. Total Messages: {len(messages)}")
        assert len(messages) == 4, "Should have 2 user + 2 AI messages in Conv A"

        print("\n=== Test 4: Switching back and Follow-up ===")
        # Message 2 on Conversation B
        await client.post(f"{BASE_URL}/tutor/chat", json={
            "session_id": session_b,
            "question": "Give me an example.",
            "document_id": None
        })
        print("Message 2 sent (Follow-up on B).")
        
        # Fetch Conversation B
        hist_b = await client.get(f"{BASE_URL}/tutor/session/{session_b}")
        print(f"Loaded Conversation B. Total Messages: {len(hist_b.json()['messages'])}")

if __name__ == "__main__":
    asyncio.run(test_flow())
