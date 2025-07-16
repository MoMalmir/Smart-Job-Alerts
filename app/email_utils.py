import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_job_matches_email(
    sender_email, sender_password, receiver_email, job_matches, keyword
):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Your Daily Matched Job Postings for : {keyword}"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create HTML content
    html = "<h2>Matched Job Opportunities:</h2><ul>"
    for job in job_matches:
        html += f"<li><b>Keyword:</b> {job['job_keyword']}<br>"
        html += f"<b>{job['title']}</b> at <b>{job['employer']}</b><br>"
        html += f"<a href='{job['url']}'>{job['url']}</a><br>"
        html += f"<i>Reason:</i> {job['reason']}</li><br><br>"
    html += "</ul>"

    message.attach(MIMEText(html, "html"))

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
