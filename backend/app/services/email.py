import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import socket
from dotenv import load_dotenv

load_dotenv()

# We will read these from the environment variables (which you can set in .env)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_EMAIL", os.getenv("SMTP_USER"))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

logger = logging.getLogger(__name__)

def print_otp_banner(email: str, otp: str, purpose: str = "Verification"):
    print("\n" + "="*60)
    print(f" EDUAGENT AI LOCAL DEV MODE - {purpose.upper()} ".center(60, "="))
    print("="*60)
    print(f" [EduAgent AI] {purpose} Code for {email}: {otp} ")
    print("="*60 + "\n")

def sendVerificationEmail(email: str, otp: str):
    """
    Sends a real email containing the 2FA verification code using Gmail SMTP.
    Safely catches exceptions so local development is not blocked by SMTP failures.
    """
    # 1. Console Fallback
    print_otp_banner(email, otp)
    
    smtp_host = SMTP_SERVER
    smtp_port = SMTP_PORT
    smtp_user = SMTP_USER.strip() if SMTP_USER else None
    smtp_pass = SMTP_PASSWORD.strip() if SMTP_PASSWORD else None
    
    if not smtp_user or not smtp_pass:
        logger.warning("SMTP credentials missing in .env. Skipping real email dispatch.")
        return False
        
    print(f"[Step 7] Attempting to send verification email via SMTP to {email}.")
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email
        msg['Subject'] = "Verify your EduAgent AI Account"
        
        body = f"Hello,\n\nYour verification code is:\n\n{otp}\n\nThis code expires in 10 minutes."
        msg.attach(MIMEText(body, 'plain'))
        
        # 2. Strict 5-second timeout
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=5)
        server.starttls()
        server.login(smtp_user, smtp_pass)
            
        text = msg.as_string()
        server.sendmail(smtp_user, email, text)
        server.quit()
        print(f"Successfully sent verification email to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {e}. Email not sent, but development can continue.")
        return False
    except (smtplib.SMTPConnectError, socket.timeout) as e:
        logger.error(f"SMTP Connection/Timeout Error: {e}. Email not sent, but development can continue.")
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {email}. Exact SMTP error: {e}")
        return False

def send_password_reset_email(to_email: str, code: str):
    """
    Sends a real email containing the password reset OTP using Gmail SMTP.
    """
    # 1. Console Fallback
    print_otp_banner(to_email, code, "Password Reset")
    
    smtp_user = SMTP_USER.strip() if SMTP_USER else None
    smtp_pass = SMTP_PASSWORD.strip() if SMTP_PASSWORD else None
    
    if not smtp_user or not smtp_pass:
        logger.warning("SMTP credentials missing. Cannot send password reset email.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = "Reset Your Password"
        
        body = f"Hello,\n\nYour 6-digit password reset code is: {code}\n\nPlease use this code to reset your password. This code expires in 10 minutes.\n\nIf you did not request this, please ignore this email.\n\nThank you,\nEduAgent AI Team"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        text = msg.as_string()
        server.sendmail(smtp_user, to_email, text)
        server.quit()
        print(f"Successfully sent password reset email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}. Development can continue.")
        return False
