import logging
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from flask import Flask, abort, redirect, request, send_from_directory, url_for


SITE_ROOT = Path(__file__).resolve().parent
CONTACT_EMAIL = "info@rjtechnologies.com"
PUBLIC_ASSET_SUFFIXES = {".css", ".gif", ".ico", ".jpeg", ".jpg", ".js", ".png", ".svg", ".webp"}
SERVICE_LABELS = {
    "web-development": "Web Development",
    "mobile-applications-and-development": "Mobile Applications and Development",
    "automation-systems": "Automation Systems",
    "networking": "Network Installation",
    "innovation-and-adaptability": "Innovation and Adaptability",
    "cyber-security": "Cyber Security",
    "cloud-solutions": "Cloud Services",
    "ui-ux-design": "UI/UX Design",
    "consulting": "IT Consulting",
}
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024


def _contact_values():
    values = {
        "First name": request.form.get("FName", "").strip(),
        "Last name": request.form.get("LName", "").strip(),
        "Email": request.form.get("email", "").strip(),
        "Phone": request.form.get("phone", "").strip(),
        "Company/business": request.form.get("company/business", "").strip(),
        "Service": request.form.get("service", "").strip(),
        "Project details": request.form.get("message", "").strip(),
    }
    limits = {
        "First name": 100,
        "Last name": 100,
        "Email": 254,
        "Phone": 40,
        "Company/business": 200,
        "Project details": 5000,
    }

    if any(not values[field] or len(values[field]) > limit for field, limit in limits.items()):
        return None
    if not EMAIL_PATTERN.fullmatch(values["Email"]):
        return None
    if values["Service"] not in SERVICE_LABELS:
        return None
    for field, value in values.items():
        allowed_controls = "\r\n\t" if field == "Project details" else ""
        if any(
            (ord(character) < 32 and character not in allowed_controls) or ord(character) == 127
            for character in value
        ):
            return None

    return values


def _send_contact_email(values):
    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    smtp_sender = os.environ.get("SMTP_FROM", "").strip()
    smtp_username = os.environ.get("SMTP_USERNAME", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    smtp_port_value = os.environ.get("SMTP_PORT", "587")

    if not smtp_host or not EMAIL_PATTERN.fullmatch(smtp_sender):
        logger.error("Contact submission could not be sent: SMTP_HOST and a valid SMTP_FROM are required.")
        return False
    if bool(smtp_username) != bool(smtp_password):
        logger.error("Contact submission could not be sent: both SMTP_USERNAME and SMTP_PASSWORD must be configured.")
        return False

    try:
        smtp_port = int(smtp_port_value)
    except ValueError:
        logger.error("Contact submission could not be sent: SMTP_PORT must be a valid port number.")
        return False

    if not 1 <= smtp_port <= 65535:
        logger.error("Contact submission could not be sent: SMTP_PORT is outside the valid range.")
        return False

    message = EmailMessage()
    message["Subject"] = f"Website inquiry: {SERVICE_LABELS[values['Service']]}"
    message["From"] = smtp_sender
    message["To"] = CONTACT_EMAIL
    message["Reply-To"] = values["Email"]
    message.set_content(
        "\n".join(
            [
                f"First name: {values['First name']}",
                f"Last name: {values['Last name']}",
                f"Email: {values['Email']}",
                f"Phone: {values['Phone']}",
                f"Company/business: {values['Company/business']}",
                f"Service: {SERVICE_LABELS[values['Service']]}",
                "",
                "Project details:",
                values["Project details"],
            ]
        )
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            if smtp_username:
                smtp.login(smtp_username, smtp_password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception("Contact submission could not be delivered by the configured SMTP server.")
        return False

    return True


@app.get("/")
@app.get("/home.html")
def home_page():
    return send_from_directory(SITE_ROOT, "home.html")


@app.get("/about.html")
def about_page():
    return send_from_directory(SITE_ROOT, "about.html")


@app.get("/services.html")
def services_page():
    return send_from_directory(SITE_ROOT, "services.html")


@app.get("/blog.html")
def blog_page():
    return send_from_directory(SITE_ROOT, "blog.html")


@app.get("/contact.html")
def contact_page():
    return send_from_directory(SITE_ROOT, "contact.html")


@app.get("/<path:asset_path>")
def public_asset(asset_path):
    if Path(asset_path).suffix.lower() not in PUBLIC_ASSET_SUFFIXES:
        abort(404)
    return send_from_directory(SITE_ROOT, asset_path)


@app.post("/contact")
def submit_contact():
    if request.form.get("company_website", "").strip():
        logger.info("Rejected an automated contact form submission.")
        return redirect(url_for("contact_page", submission="invalid"), code=303)

    values = _contact_values()
    if values is None:
        logger.info("Rejected a contact form submission because one or more fields were invalid.")
        return redirect(url_for("contact_page", submission="invalid"), code=303)

    if not _send_contact_email(values):
        return redirect(url_for("contact_page", submission="error"), code=303)

    logger.info("Delivered a contact form submission to the configured recipient.")
    return redirect(url_for("contact_page", submission="sent"), code=303)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
