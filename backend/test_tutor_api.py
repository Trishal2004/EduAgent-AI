import asyncio
import httpx
import uuid
import pymysql

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def get_auth_token():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPassword123!"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Register
        resp = await client.post(f"{BASE_URL}/auth/register", json={
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
    print("=== Getting Auth Token ===")
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        # 1. Create a session
        print("\n=== Testing POST /tutor/session ===")
        resp = await client.post(f"{BASE_URL}/tutor/session")
        print(f"Status: {resp.status_code}")
        session_id = resp.json()["id"]
        print(f"Created Session ID: {session_id}")

        # 2. Get history
        print("\n=== Testing GET /tutor/history ===")
        resp = await client.get(f"{BASE_URL}/tutor/history")
        print(f"Status: {resp.status_code}")
        print(f"Sessions count: {len(resp.json())}")

        # 3. Rename session
        print("\n=== Testing PUT /tutor/session/{id}/rename ===")
        resp = await client.put(f"{BASE_URL}/tutor/session/{session_id}/rename", json={"title": "Test Title"})
        print(f"Status: {resp.status_code}")
        print(f"New Title: {resp.json().get('title')}")

        # 4. Get specific session
        print(f"\n=== Testing GET /tutor/session/{session_id} ===")
        resp = await client.get(f"{BASE_URL}/tutor/session/{session_id}")
        print(f"Status: {resp.status_code}")
        print(f"Messages count: {len(resp.json().get('messages', []))}")

        # 5. Send message
        print("\n=== Testing POST /tutor/chat ===")
        resp = await client.post(f"{BASE_URL}/tutor/chat", json={
            "session_id": session_id,
            "question": "What is AI?",
            "document_id": None
        })
        print(f"Status: {resp.status_code}")
        if resp.status_code == 500:
            print(f"Expected 500 due to invalid OpenAI Key: {resp.json()}")

        # 6. Delete session
        print(f"\n=== Testing DELETE /tutor/session/{session_id} ===")
        resp = await client.delete(f"{BASE_URL}/tutor/session/{session_id}")
        print(f"Status: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(test_flow())
