"""
Email service for sending verification and password reset emails.
Uses SMTP configuration from settings.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending various types of emails."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.email_from_name = settings.EMAIL_FROM_NAME
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content
            text_content: Plain text content (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.email_from_name} <{self.email_from}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


# Global email service instance
email_service = EmailService()


def send_verification_email(email: str, name: str, token: str) -> bool:
    """
    Send email verification email.
    
    Args:
        email: User's email address
        name: User's name
        token: Verification token
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Welcome to TrueFit - Verify Your Email"
    
    # For development, you might want to use a simple verification URL
    # In production, this should be your frontend URL
    verification_url = f"http://localhost:3000/verify-email?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Email Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4A90E2;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .button {{
                display: inline-block;
                background-color: #4A90E2;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Welcome to TrueFit!</h1>
        </div>
        <div class="content">
            <h2>Hello {name},</h2>
            <p>Thank you for joining TrueFit, the recruitment platform that finds the perfect match between employers and employees based on comprehensive compatibility.</p>
            <p>To complete your registration, please verify your email address by clicking the button below:</p>
            <a href="{verification_url}" class="button">Verify Email Address</a>
            <p>Or copy and paste this link into your browser:</p>
            <p><a href="{verification_url}">{verification_url}</a></p>
            <p>This verification link will expire in 1 hour for security reasons.</p>
            <p>If you didn't create an account with TrueFit, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The TrueFit Team</p>
            <p>This is an automated email. Please do not reply to this message.</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to TrueFit!
    
    Hello {name},
    
    Thank you for joining TrueFit, the recruitment platform that finds the perfect match between employers and employees based on comprehensive compatibility.
    
    To complete your registration, please verify your email address by visiting:
    {verification_url}
    
    This verification link will expire in 1 hour for security reasons.
    
    If you didn't create an account with TrueFit, please ignore this email.
    
    Best regards,
    The TrueFit Team
    """
    
    return email_service.send_email(email, subject, html_content, text_content)


def send_password_reset_email(email: str, name: str, token: str) -> bool:
    """
    Send password reset email.
    
    Args:
        email: User's email address
        name: User's name
        token: Password reset token
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "TrueFit - Password Reset Request"
    
    # For development, you might want to use a simple reset URL
    # In production, this should be your frontend URL
    reset_url = f"http://localhost:3000/reset-password?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Password Reset</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #FF6B6B;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .button {{
                display: inline-block;
                background-color: #FF6B6B;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
                font-size: 12px;
            }}
            .warning {{
                background-color: #FFF3CD;
                border: 1px solid #FFEAA7;
                color: #856404;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>
        <div class="content">
            <h2>Hello {name},</h2>
            <p>We received a request to reset your password for your TrueFit account.</p>
            <p>To reset your password, click the button below:</p>
            <a href="{reset_url}" class="button">Reset Password</a>
            <p>Or copy and paste this link into your browser:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <div class="warning">
                <strong>Important:</strong> This password reset link will expire in 30 minutes for security reasons.
            </div>
            <p>If you didn't request a password reset, please ignore this email and your password will remain unchanged.</p>
            <p>For security reasons, never share this link with anyone.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The TrueFit Team</p>
            <p>This is an automated email. Please do not reply to this message.</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Password Reset Request
    
    Hello {name},
    
    We received a request to reset your password for your TrueFit account.
    
    To reset your password, visit:
    {reset_url}
    
    This password reset link will expire in 30 minutes for security reasons.
    
    If you didn't request a password reset, please ignore this email and your password will remain unchanged.
    
    For security reasons, never share this link with anyone.
    
    Best regards,
    The TrueFit Team
    """
    
    return email_service.send_email(email, subject, html_content, text_content)


def send_welcome_email(email: str, name: str, role: str) -> bool:
    """
    Send welcome email after successful email verification.
    
    Args:
        email: User's email address
        name: User's name
        role: User's role (candidate or employer)
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Welcome to TrueFit - Your Account is Ready!"
    
    # Customize content based on role
    if role == "candidate":
        role_content = """
        <h3>What's Next for You:</h3>
        <ul>
            <li>Complete your candidate profile</li>
            <li>Take our personality and values assessment</li>
            <li>Upload your resume and portfolio</li>
            <li>Start exploring job opportunities</li>
            <li>Connect with employers who match your values</li>
        </ul>
        """
    else:  # employer
        role_content = """
        <h3>What's Next for You:</h3>
        <ul>
            <li>Complete your company profile</li>
            <li>Add your company culture and values</li>
            <li>Post your first job opening</li>
            <li>Start discovering qualified candidates</li>
            <li>Find talent that aligns with your company culture</li>
        </ul>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Welcome to TrueFit</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .button {{
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 Welcome to TrueFit!</h1>
        </div>
        <div class="content">
            <h2>Hello {name},</h2>
            <p>Congratulations! Your email has been verified and your TrueFit account is now active.</p>
            <p>TrueFit is more than just a recruitment platform - we're revolutionizing how employers and employees connect by focusing on comprehensive compatibility, including values, culture, and personality alignment.</p>
            {role_content}
            <a href="http://localhost:3000/dashboard" class="button">Get Started</a>
            <p>If you have any questions or need assistance, our support team is here to help.</p>
            <p>Welcome aboard, and let's find your perfect match!</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The TrueFit Team</p>
            <p>Need help? Contact us at support@truefit.com</p>
        </div>
    </body>
    </html>
    """
    
    return email_service.send_email(email, subject, html_content)