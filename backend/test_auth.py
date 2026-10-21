import asyncio
import httpx
import uuid
import sqlite3

BASE_URL = "http://127.0.0.1:8000/api/v1/auth"
DB_PATH = "/Users/k.trishal/Desktop/EduAgent AI/backend/eduagent.db"

async def test_flow():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPassword123!"
    
    print(f"=== Testing Registration for {email} ===")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register
        resp = await client.post(f"{BASE_URL}/register", json={
            "email": email,
            "password": password,
            "password_confirm": password
        })
        print(f"Register Response: {resp.status_code}, {resp.text}")
        if resp.status_code != 201:
            print("Failed to register")
            return
            
        # 2. Unverified Login
        print("\n=== Testing Unverified Login ===")
        login_resp = await client.post(f"{BASE_URL}/login", json={
            "email": email,
            "password": password
        })
        print(f"Login Response (Unverified): {login_resp.status_code}, {login_resp.text}")
        
        # 3. Get OTP from DB (to simulate receiving email)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT verification_otp FROM users WHERE email = ?", (email,))
        otp = cur.fetchone()[0]
        print(f"\n=== OTP retrieved from DB: {otp} ===")
        
        # 4. Wrong OTP
        print("\n=== Testing Wrong OTP ===")
        wrong_otp = "000000" if otp != "000000" else "111111"
        verify_resp_wrong = await client.post(f"{BASE_URL}/verify-email", json={
            "email": email,
            "otp": wrong_otp
        })
        print(f"Verify Wrong OTP: {verify_resp_wrong.status_code}, {verify_resp_wrong.text}")
        
        # 5. Expired OTP
        print("\n=== Testing Expired OTP ===")
        # Manually expire it in DB
        cur.execute("UPDATE users SET otp_expiry = '2020-01-01 00:00:00.000000' WHERE email = ?", (email,))
        conn.commit()
        
        verify_resp_expired = await client.post(f"{BASE_URL}/verify-email", json={
            "email": email,
            "otp": otp
        })
        print(f"Verify Expired OTP: {verify_resp_expired.status_code}, {verify_resp_expired.text}")
        
        # 6. Resend OTP
        print("\n=== Testing Resend OTP ===")
        resend_resp = await client.post(f"{BASE_URL}/resend-otp", json={
            "email": email
        })
        print(f"Resend Response: {resend_resp.status_code}, {resend_resp.text}")
        
        # Get new OTP
        cur.execute("SELECT verification_otp FROM users WHERE email = ?", (email,))
        new_otp = cur.fetchone()[0]
        print(f"New OTP retrieved from DB: {new_otp}")
        
        # 7. Correct Verification
        print("\n=== Testing Correct OTP ===")
        verify_resp_correct = await client.post(f"{BASE_URL}/verify-email", json={
            "email": email,
            "otp": new_otp
        })
        print(f"Verify Correct OTP: {verify_resp_correct.status_code}, {verify_resp_correct.text}")
        
        # 8. Verified Login
        print("\n=== Testing Verified Login ===")
        login_resp_success = await client.post(f"{BASE_URL}/login", json={
            "email": email,
            "password": password
        })
        print(f"Login Response (Verified): {login_resp_success.status_code}")
        if login_resp_success.status_code == 200:
            print("Successfully authenticated and got JWT.")
            
        conn.close()

if __name__ == "__main__":
    asyncio.run(test_flow())
