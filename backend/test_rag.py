import asyncio
import httpx
import uuid
import pymysql

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def get_auth_token():
    email = f"test_rag_{uuid.uuid4().hex[:8]}@example.com"
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

async def test_rag_flow():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
        resp = await client.post(f"{BASE_URL}/tutor/session")
        session_id = resp.json()["id"]

        tests = [
            ("1. General question", "What is Python?", None),
            ("2. Document-specific question", "According to my DBMS PDF, explain normalization.", None),
            ("3. Specific uploaded document", "Explain the document context.", "12345678-1234-5678-1234-567812345678"),
            ("4. Multiple chunks required", "According to the pdf, summarize everything.", None),
            ("5. Follow-up document question", "Can you give another example from the document?", None),
            ("6. No relevant document", "What does the empty document say?", None),
        ]
        
        for name, q, doc_id in tests:
            print(f"\n=== Test: {name} ===")
            print(f"User: {q}")
            resp = await client.post(f"{BASE_URL}/tutor/chat", json={
                "session_id": session_id,
                "question": q,
                "document_id": doc_id
            })
            
            if resp.status_code == 200:
                print("Success!")
                print("Content preview:", str(resp.json().get("ai_message", {}).get("structured_data", {}))[:100])
            else:
                print(f"Failed: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_rag_flow())
