from flask import Blueprint, request
import smtplib
from app.models.responses import (
    SendEmailResponse,
)

# Blueprint Example for Scalability
bp = Blueprint('email', __name__)

@bp.route('/send-email', methods=['POST'])
def send_email():
    new_user = request.json.get('newUser')

    # Email configuration
    sender_email = "outcome-toolkit-accounts@example.com"
    recipient_email = "outcome-toolkit-accounts@example.com"
    subject = "New Team Member Request"
    body = f"New team member request: \n\n Email: {new_user['email']} " \
       f"\n First Name: {new_user['first_name']} \n Last Name: {new_user['last_name']}" \
       f"\n Company: {new_user['company']} \n Project Name: {new_user['project_name']}" \
        f"\n Project Id: {new_user['project_id']}"

    email_message = f"Subject: {subject}\n\n{body}"

    try:
        # Connect to the SMTP server and send email
        with smtplib.SMTP("localhost", 25) as server:
            server.sendmail(sender_email, recipient_email, email_message)
    except Exception as e:
        return f"Failed to send email: {str(e)}"
    
    response = SendEmailResponse(
            message="Email sent successfully",
        )
    return response.to_response(status_code=201)