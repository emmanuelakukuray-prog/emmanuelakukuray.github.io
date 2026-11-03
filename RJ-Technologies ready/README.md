# RJ-Technologies website

## Run locally

Install Python 3.9 or newer, then run these commands from this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000` in a browser. The Flask app serves the five HTML pages and their public image, CSS, and JavaScript assets.

## Configure contact email delivery

The contact form sends submissions to `info@rjtechnologies.com`. Configure the SMTP settings in the server environment before starting the app. Never put mail credentials in HTML, JavaScript, or source control.

```powershell
$env:SMTP_HOST = "smtp.example.com"
$env:SMTP_PORT = "587"
$env:SMTP_FROM = "website@example.com"
$env:SMTP_USERNAME = "website@example.com"
$env:SMTP_PASSWORD = "your-provider-app-password"
python app.py
```

SMTP is connected using STARTTLS. `SMTP_USERNAME` and `SMTP_PASSWORD` may both be omitted if the SMTP server does not require authentication. Without valid `SMTP_HOST` and `SMTP_FROM` settings, the server logs the configuration error and reports that the message could not be sent.

For deployment, start the production WSGI server with `waitress-serve --listen=127.0.0.1:5000 app:app`, then route HTTPS traffic to it through a reverse proxy. Apply rate limiting to `POST /contact` at the proxy, and do not expose Flask's development server directly to the internet.

## Run backend tests

```powershell
.\.venv\Scripts\python.exe -m unittest
```
