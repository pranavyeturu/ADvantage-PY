import csv
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from dotenv import load_dotenv
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT   = int(os.getenv("SMTP_PORT"))  # cast to int if needed
USERNAME    = os.getenv("USERNAME")
PASSWORD    = os.getenv("PASSWORD")
# or OAuth2-backed app password

# ——— Logging setup ———
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def send_email(to_address: str, subject: str, body: str) -> dict:
    """
    Sends a plain-text email via SMTP.
    Returns a dict {success:bool, error:str|None}.
    """
    msg = MIMEMultipart()
    msg["From"]    = USERNAME
    msg["To"]      = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        logger.info(f"Connecting to SMTP {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent to {to_address}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to send email to {to_address}: {e}")
        return {"success": False, "error": str(e)}

def send_emails_from_csv(csv_path: str, subject: str, body: str, column: str="email") -> dict:
    """
    Reads email addresses from a CSV and sends the same message to each.
    Returns summary: {total, sent, failed, errors:[{email,error}]}
    """
    summary = {"total":0, "sent":0, "failed":0, "errors":[]}

    if not os.path.isfile(csv_path):
        err = f"CSV not found: {csv_path}"
        logger.error(err)
        return {"error": err}

    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if column not in reader.fieldnames:
            err = f"Column '{column}' not in CSV; fields={reader.fieldnames}"
            logger.error(err)
            return {"error": err}

        for row in reader:
            summary["total"] += 1
            email = row[column].strip()
            result = send_email(email, subject, body)
            if result.get("success"):
                summary["sent"] += 1
            else:
                summary["failed"] += 1
                summary["errors"].append({"email": email, "error": result.get("error")})

    logger.info(f"CSV email blast complete: {summary}")
    return summary
