import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

def test_smtp_configuration():
    print("="*50)
    print("SMTP CONFIGURATION TEST SCRIPT")
    print("="*50)
    
    # 1. Load the exact environment as FastAPI
    load_dotenv()
    
    # 2. Extract configuration, stripping whitespaces to avoid copy-paste errors
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    # Try SMTP_EMAIL first (as in your .env), then fallback to SMTP_USER
    smtp_email = os.getenv("SMTP_EMAIL", os.getenv("SMTP_USER"))
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    smtp_email = smtp_email.strip() if smtp_email else None
    smtp_password = smtp_password.strip() if smtp_password else None
    
    print(f"Loading variables from .env...")
    print(f"Email: {smtp_email}")
    print(f"Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
    
    if not smtp_email or not smtp_password:
        print("\n[FAILED] SMTP_EMAIL or SMTP_PASSWORD is not set in .env")
        return
        
    print("\nAttempting to connect to smtp.gmail.com:587...")
    try:
        # 3. Create the test message
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = "k70132172@gmail.com"
        msg['Subject'] = "EduAgent AI - SMTP Diagnostics Test"
        
        body = "If you are reading this, your EduAgent AI SMTP configuration is working perfectly!"
        msg.attach(MIMEText(body, 'plain'))
        
        # 4. Connect, authenticate, and send
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1) # This prints all SMTP communication to the terminal
        
        server.starttls()
        print("\nTLS Connection Established. Authenticating...")
        
        server.login(smtp_email, smtp_password)
        print("\nAuthentication Successful!")
        
        server.sendmail(smtp_email, "k70132172@gmail.com", msg.as_string())
        server.quit()
        
        print("\n[SUCCESS] Test email successfully dispatched to k70132172@gmail.com")
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n[FAILED] Authentication Error.")
        print("This usually means you are using your standard Google password instead of an App Password, or you have 2FA disabled.")
        print(f"Exact Error: {e}")
    except smtplib.SMTPServerDisconnected as e:
        print(f"\n[FAILED] Server Disconnected Unexpectedly.")
        print(f"Exact Error: {e}")
    except Exception as e:
        print(f"\n[FAILED] An unexpected error occurred.")
        print(f"Exact Error: {e}")

if __name__ == "__main__":
    test_smtp_configuration()
