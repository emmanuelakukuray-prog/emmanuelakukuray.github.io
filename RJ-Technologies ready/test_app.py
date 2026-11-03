import os
import smtplib
import unittest
from unittest.mock import patch

import app as site


VALID_FORM = {
    "FName": "Ada",
    "LName": "Lovelace",
    "email": "ada@example.com",
    "phone": "+211 922 666 205",
    "company/business": "Analytical Engines",
    "service": "web-development",
    "message": "I would like to discuss a website project.",
}
SMTP_SETTINGS = {
    "SMTP_HOST": "smtp.example.com",
    "SMTP_PORT": "587",
    "SMTP_FROM": "website@example.com",
    "SMTP_USERNAME": "website@example.com",
    "SMTP_PASSWORD": "test-password",
}


class SiteRoutesTests(unittest.TestCase):
    def setUp(self):
        site.app.config["TESTING"] = True
        self.client = site.app.test_client()

    def test_pages_and_public_assets_are_served(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        for page in ("home.html", "about.html", "services.html", "blog.html", "contact.html"):
            with self.subTest(page=page):
                self.assertEqual(self.client.get(f"/{page}").status_code, 200)

        self.assertEqual(self.client.get("/style.css").status_code, 200)
        self.assertEqual(self.client.get("/app.py").status_code, 404)
        self.assertEqual(self.client.get("/README.md").status_code, 404)
        self.assertEqual(self.client.get("/../app.py").status_code, 404)


class ContactSubmissionTests(unittest.TestCase):
    def setUp(self):
        site.app.config["TESTING"] = True
        self.client = site.app.test_client()

    @patch.dict(os.environ, SMTP_SETTINGS, clear=False)
    @patch("app.smtplib.SMTP")
    def test_valid_submission_is_emailed(self, smtp_factory):
        smtp = smtp_factory.return_value.__enter__.return_value

        response = self.client.post("/contact", data=VALID_FORM)

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/contact.html?submission=sent"))
        smtp.starttls.assert_called_once()
        smtp.login.assert_called_once_with("website@example.com", "test-password")
        sent_message = smtp.send_message.call_args.args[0]
        self.assertEqual(sent_message["To"], "info@rjtechnologies.com")
        self.assertEqual(sent_message["Reply-To"], "ada@example.com")
        self.assertIn("Analytical Engines", sent_message.get_content())

    @patch.dict(os.environ, {}, clear=True)
    @patch("app.smtplib.SMTP")
    def test_invalid_submission_is_rejected_without_sending(self, smtp_factory):
        invalid_form = {**VALID_FORM, "email": "not-an-email"}

        response = self.client.post("/contact", data=invalid_form)

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/contact.html?submission=invalid"))
        smtp_factory.assert_not_called()

    @patch.dict(os.environ, SMTP_SETTINGS, clear=False)
    @patch("app.smtplib.SMTP")
    def test_honeypot_rejects_automated_submission(self, smtp_factory):
        automated_form = {**VALID_FORM, "company_website": "spam.example"}

        response = self.client.post("/contact", data=automated_form)

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/contact.html?submission=invalid"))
        smtp_factory.assert_not_called()

    @patch.dict(os.environ, {}, clear=True)
    @patch("app.smtplib.SMTP")
    def test_missing_smtp_configuration_reports_failure(self, smtp_factory):
        response = self.client.post("/contact", data=VALID_FORM)

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/contact.html?submission=error"))
        smtp_factory.assert_not_called()

    @patch.dict(os.environ, SMTP_SETTINGS, clear=False)
    @patch("app.smtplib.SMTP")
    def test_smtp_failure_is_reported_without_claiming_success(self, smtp_factory):
        smtp = smtp_factory.return_value.__enter__.return_value
        smtp.send_message.side_effect = smtplib.SMTPException("delivery failed")

        response = self.client.post("/contact", data=VALID_FORM)

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/contact.html?submission=error"))


if __name__ == "__main__":
    unittest.main()
