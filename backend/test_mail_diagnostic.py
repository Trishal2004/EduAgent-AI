import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
import socket
from dotenv import load_dotenv

def run_smtp_diagnostic():
    print("="*60)
    print(" EDUAGENT AI - SMTP DIAGNOSTIC SUITE ".center(60, "="))
    print("="*60)
    
    # 1. Configuration Validation
    print("[1] Loading environment variables...")
    load_dotenv()
    
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_EMAIL = os.getenv("SMTP_EMAIL", os.getenv("SMTP_USER"))
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("\n[CRITICAL ERROR] SMTP_EMAIL or SMTP_PASSWORD not found in .env")
        sys.exit(1)
        
    # 2. Sanitization
    print("[2] Sanitizing credentials...")
    SMTP_EMAIL = SMTP_EMAIL.strip()
    SMTP_PASSWORD = SMTP_PASSWORD.strip()
    
    print(f"    Target Server : {SMTP_SERVER}:{SMTP_PORT}")
    print(f"    Sender Email  : {SMTP_EMAIL}")
    print(f"    Password Auth : {'*' * len(SMTP_PASSWORD)} (Length: {len(SMTP_PASSWORD)})")
    
    # 3 & 4 & 5. Execution
    try:
        print("\n[3] Building HTML Email Payload...")
        msg = MIMEMultipart("alternative")
        msg['From'] = SMTP_EMAIL
        msg['To'] = "k70132172@gmail.com"
        msg['Subject'] = "EduAgent AI - Security Verification"
        
        # EduAgent AI styled HTML OTP payload
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f5; padding: 20px;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #111827; text-align: center;">EduAgent AI Security</h2>
                    <p style="color: #4b5563; font-size: 16px;">Hello,</p>
                    <p style="color: #4b5563; font-size: 16px;">We are running a diagnostic test. Your mock verification code is:</p>
                    
                    <div style="background-color: #f3f4f6; border: 1px solid #e5e7eb; padding: 20px; text-align: center; border-radius: 8px; margin: 30px 0;">
                        <h1 style="color: #4f46e5; letter-spacing: 8px; margin: 0; font-size: 36px;">749102</h1>
                    </div>
                    
                    <p style="color: #6b7280; font-size: 14px; text-align: center;">This is an automated diagnostic test from EduAgent AI.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))
        
        print("\n[4] Initiating SMTP Handshake (Verbose Mode Enabled)...")
        print("-" * 60)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        
        # 3. Verbose Debugging
        server.set_debuglevel(1)
        
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        print("\n[5] Authenticating...")
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        
        print("\n[6] Sending Email Payload...")
        server.sendmail(SMTP_EMAIL, "k70132172@gmail.com", msg.as_string())
        
        server.quit()
        print("-" * 60)
        print("\n[SUCCESS] The diagnostic email was dispatched successfully to k70132172@gmail.com!")
        
    # 6. Explicit Error Handling
    except smtplib.SMTPAuthenticationError as e:
        print("-" * 60)
        print(f"\n[FAILED] SMTP Authentication Error (Code {e.smtp_code})")
        print("Reason: Google rejected your credentials.")
        print("Fixes: \n 1. Ensure you generated a 16-digit 'App Password', NOT your standard Google password.\n 2. Ensure 2-Step Verification is ON in your Google account.")
        print(f"Detailed Error: {e.smtp_error.decode('utf-8') if isinstance(e.smtp_error, bytes) else e.smtp_error}")
        
    except (smtplib.SMTPConnectError, socket.timeout) as e:
        print("-" * 60)
        print("\n[FAILED] Network Connection or Timeout Error")
        print(f"Reason: Unable to reach {SMTP_SERVER} on port {SMTP_PORT}. Your ISP, firewall, or VPN might be blocking outgoing port 587.")
        print(f"Detailed Error: {e}")
        
    except Exception as e:
        print("-" * 60)
        print("\n[FAILED] Unhandled Diagnostic Exception")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Detailed Error: {e}")

if __name__ == "__main__":
    run_smtp_diagnostic()
