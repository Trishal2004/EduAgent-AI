import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_otp_email(to_email: str, otp_code: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", "EduAgent AI")

    if not smtp_email or not smtp_password:
        print("Warning: SMTP credentials not set. Simulating email sending.")
        print(f"--- EMAIL TO: {to_email} ---")
        print(f"--- OTP CODE: {otp_code} ---")
        return True

    msg = MIMEMultipart("alternative")
    msg['From'] = f"{email_from} <{smtp_email}>"
    msg['To'] = to_email
    msg['Subject'] = "Your Login Verification Code"

    # Plain text fallback
    text = f"""
    EduAgent AI
    
    Your Login Verification Code

    Your one-time password (OTP) is: {otp_code}
    
    This code will expire in 5 minutes.
    
    If you did not request this code, please ignore this email.
    """

    # HTML Version
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Login Verification Code</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f3f4f6;
                margin: 0;
                padding: 0;
                color: #1f2937;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                border: 1px solid #e5e7eb;
            }}
            .header {{
                background-color: #f8fafc;
                padding: 24px;
                text-align: center;
                border-bottom: 1px solid #e5e7eb;
            }}
            .header h1 {{
                margin: 0;
                color: #2563eb;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.025em;
            }}
            .content {{
                padding: 32px 24px;
                text-align: center;
            }}
            .content h2 {{
                margin-top: 0;
                color: #111827;
                font-size: 20px;
                font-weight: 600;
            }}
            .content p {{
                color: #4b5563;
                font-size: 16px;
                line-height: 1.5;
                margin-bottom: 24px;
            }}
            .otp-container {{
                background-color: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 8px;
                padding: 24px;
                margin: 0 auto 24px;
                max-width: 300px;
            }}
            .otp-code {{
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
                font-size: 36px;
                font-weight: 700;
                color: #166534;
                letter-spacing: 8px;
                margin: 0;
            }}
            .footer {{
                background-color: #f8fafc;
                padding: 24px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
            }}
            .footer p {{
                margin: 0;
                color: #6b7280;
                font-size: 14px;
                line-height: 1.5;
            }}
            
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {{
                body {{
                    background-color: #111827;
                }}
                .container {{
                    background-color: #1f2937;
                    border-color: #374151;
                }}
                .header, .footer {{
                    background-color: #1f2937;
                    border-color: #374151;
                }}
                .content h2 {{
                    color: #f9fafb;
                }}
                .content p {{
                    color: #d1d5db;
                }}
                .otp-container {{
                    background-color: #064e3b;
                    border-color: #065f46;
                }}
                .otp-code {{
                    color: #34d399;
                }}
                .footer p {{
                    color: #9ca3af;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>EduAgent AI</h1>
            </div>
            
            <div class="content">
                <h2>Your Login Verification Code</h2>
                <p>Please use the following 6-digit code to complete your secure sign-in process.</p>
                
                <div class="otp-container">
                    <p class="otp-code">{otp_code}</p>
                </div>
                
                <p style="font-size: 14px; color: #6b7280;">This code will securely expire in <strong>5 minutes</strong>.</p>
            </div>
            
            <div class="footer">
                <p>If you did not request this code, your account is still secure. You can safely ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
