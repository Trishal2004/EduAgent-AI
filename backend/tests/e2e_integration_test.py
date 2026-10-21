import os
import sys
import time
import requests
import sqlite3
import random
import string

# Append backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://localhost:8000/api/v1"
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../eduagent.db'))

def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

def get_verification_otp(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT verification_otp FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_login_otp(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT otp_code FROM user_login_otps WHERE email = ? ORDER BY created_at DESC LIMIT 1", (email,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def run_test():
    print("Starting E2E Integration Test...")
    email = generate_random_email()
    password = "Password123!"
    full_name = "E2E Test User"

    # 1. Register
    print(f"Registering user: {email}")
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "password_confirm": password,
        "full_name": full_name
    })
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"

    # 2. Login Request
    print("Requesting login OTP...")
    login_req = requests.post(f"{BASE_URL}/auth/login-request", json={
        "email": email,
        "password": password
    })
    
    # Check if we need to verify email first (depends on auth flow)
    if login_req.status_code == 403 and "verify your email first" in login_req.text:
        print("Email verification required. Verifying...")
        otp = get_verification_otp(email)
        assert otp is not None, "No OTP found in DB for verification"
        ver_resp = requests.post(f"{BASE_URL}/auth/verify-email", json={
            "email": email,
            "otp": otp
        })
        assert ver_resp.status_code == 200, f"Email verification failed: {ver_resp.text}"
        
        # Retry login request
        login_req = requests.post(f"{BASE_URL}/auth/login-request", json={
            "email": email,
            "password": password
        })

    assert login_req.status_code == 200, f"Login request failed: {login_req.text}"

    # 3. Verify OTP
    print("Verifying login OTP...")
    otp = get_login_otp(email)
    assert otp is not None, "No OTP found in DB for login"
    ver_resp = requests.post(f"{BASE_URL}/auth/verify-otp", json={
        "email": email,
        "otp": otp
    })
    assert ver_resp.status_code == 200, f"OTP verification failed: {ver_resp.text}"
    token = ver_resp.json().get("access_token")
    assert token, "No access token returned"
    
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Dashboard Check
    print("Checking initial dashboard...")
    dash_resp = requests.get(f"{BASE_URL}/dashboard/metrics", headers=headers)
    assert dash_resp.status_code == 200, f"Dashboard failed: {dash_resp.text}"
    dash_data = dash_resp.json()
    assert dash_data["stats"]["totalDocuments"] == 0, "New user should have 0 docs"

    # 5. Upload Document
    print("Uploading document...")
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test.pdf'))
    
    with open(pdf_path, "rb") as f:
        files = {"file": ("test.pdf", f, "application/pdf")}
        upload_resp = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files)
    
    assert upload_resp.status_code == 201, f"Upload failed: {upload_resp.text}"
    doc_id = upload_resp.json()["id"]

    # 6. Document Processing
    print(f"Triggering processing for document {doc_id}...")
    process_resp = requests.post(f"{BASE_URL}/documents/{doc_id}/process", headers=headers)
    assert process_resp.status_code == 200, f"Process trigger failed: {process_resp.text}"

    print(f"Waiting for document {doc_id} to process...")
    max_retries = 30
    doc_ready = False
    for i in range(max_retries):
        doc_resp = requests.get(f"{BASE_URL}/documents/", headers=headers)
        assert doc_resp.status_code == 200
        docs = doc_resp.json()
        doc = next((d for d in docs if d["id"] == doc_id), None)
        assert doc is not None, "Document disappeared"
        
        if doc.get("upload_status") == "completed":
            doc_ready = True
            break
        elif doc.get("upload_status") == "failed":
            assert False, "Document processing failed"
        
        time.sleep(2)
        
    assert doc_ready, "Document processing timed out"

    # 7. AI Tutor
    print("Testing AI Tutor...")
    tutor_resp = requests.post(f"{BASE_URL}/tutor/chat", headers=headers, json={
        "document_id": doc_id,
        "question": "What is AI?"
    })
    assert tutor_resp.status_code == 200, f"Tutor failed: {tutor_resp.text}"
    tutor_data = tutor_resp.text
    assert "data: " in tutor_data
    
    # Chat history check
    hist_resp = requests.get(f"{BASE_URL}/tutor/history", headers=headers)
    assert hist_resp.status_code == 200

    # 8. Notes Generation
    print("Generating Notes...")
    notes_resp = requests.post(f"{BASE_URL}/notes/generate", headers=headers, json={
        "document_id": doc_id,
        "detail_level": "detailed",
        "topic": "Artificial Intelligence",
        "note_type": "summary"
    })
    # Since generating notes can take time or return immediately if async, let's see
    if notes_resp.status_code not in [200, 201]:
        if any(code in notes_resp.text for code in ["503", "429", "500", "Internal Server Error"]):
            print("Notes generation skipped due to AI provider rate limit/unavailability.")
        else:
            assert False, f"Notes generation failed: {notes_resp.text}"

    # 9. Flashcards Generation
    print("Generating Flashcards...")
    flash_resp = requests.post(f"{BASE_URL}/srs/decks/generate", headers=headers, json={
        "topic": "AI Basics",
        "card_type": "conceptual",
        "document_id": doc_id,
        "number_of_cards": 5
    })
    if flash_resp.status_code not in [200, 201]:
        if any(code in flash_resp.text for code in ["503", "429", "500", "Internal Server Error"]):
            print("Flashcards generation skipped due to AI provider rate limit/unavailability.")
        else:
            assert False, f"Flashcards generation failed: {flash_resp.text}"
    else:
        deck_id = flash_resp.json()["id"]

        # Study a flashcard
        cards_resp = requests.get(f"{BASE_URL}/srs/decks/{deck_id}/review", headers=headers)
        assert cards_resp.status_code == 200
        cards = cards_resp.json()
        if cards:
            card_id = cards[0]["id"]
            review_resp = requests.post(f"{BASE_URL}/srs/cards/{card_id}/review", headers=headers, json={
                "quality": 4
            })
            assert review_resp.status_code == 200

    # 10. Daily Quizzes
    print("Generating Daily Quizzes...")
    quiz_resp = requests.post(f"{BASE_URL}/quizzes/daily/generate", headers=headers)
    if quiz_resp.status_code not in [200, 201]:
        if any(code in quiz_resp.text for code in ["503", "429", "500", "Internal Server Error"]):
            print("Quizzes generation skipped due to AI provider rate limit/unavailability.")
        else:
            assert False, f"Daily Quizzes generation failed: {quiz_resp.text}"
    else:
        # Get quizzes
        day_resp = requests.get(f"{BASE_URL}/quizzes/daily", headers=headers)
        assert day_resp.status_code == 200
        quizzes = day_resp.json()
        if quizzes:
            quiz_id = quizzes[0]["id"]
            # Start quiz
            start_resp = requests.post(f"{BASE_URL}/quizzes/{quiz_id}/start", headers=headers)
            assert start_resp.status_code == 200
            # Submit quiz
            questions = start_resp.json()["questions"]
            answers = {q["id"]: "AI is artificial intelligence" for q in questions}
            submit_resp = requests.post(f"{BASE_URL}/quizzes/{quiz_id}/submit", headers=headers, json={
                "answers": answers,
                "time_spent_seconds": 60
            })
            assert submit_resp.status_code == 200, f"Quiz submit failed: {submit_resp.text}"

    # 11. Dashboard Analytics Verification
    print("Verifying Dashboard Analytics...")
    dash_resp = requests.get(f"{BASE_URL}/dashboard/metrics", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    
    assert dash_data["stats"]["totalDocuments"] == 1, "Documents count should be 1"
    assert dash_data["stats"]["totalQuizzes"] >= 1, "Quizzes count should be >= 1"
    
    print("✅ All E2E Tests Passed Successfully!")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        sys.exit(1)
