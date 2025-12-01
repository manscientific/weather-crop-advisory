from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Store subscribers in memory
subscribers = []

# -------------- Pydantic model --------------
class EmailRequest(BaseModel):
    email: str
    city: str = "Delhi"


@app.post("/subscribe-weather-alert")
def subscribe(req: EmailRequest):
    subscribers.append({"email": req.email, "city": req.city})
    return {"message": "Subscription successful!"}


# ------------------------------------------------------
# SEND EMAIL WITH LOGS
# ------------------------------------------------------
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")

    except Exception as e:
        print("Email error:", e)


# ------------------------------------------------------
# HARSH WEATHER DETECTOR
# ------------------------------------------------------
def detect_harsh_weather(weather_item):
    temp = weather_item["main"]["temp"] - 273.15
    wind = weather_item["wind"]["speed"]
    rain = weather_item.get("rain", {}).get("3h", 0)
    condition = weather_item["weather"][0]["main"].lower()

    alerts = []

    if temp >= 40:
        alerts.append("🔥 Heatwave")
    if temp <= 5:
        alerts.append("🥶 Cold wave")
    if wind >= 15:
        alerts.append("💨 Strong wind")
    if rain >= 20:
        alerts.append("🌧 Heavy rainfall")
    if "storm" in condition:
        alerts.append("⛈ Storm coming")
    if "snow" in condition:
        alerts.append("❄ Snowfall")

    return alerts


# ------------------------------------------------------
# WEATHER CHECKER (AUTOMATIC)
# ------------------------------------------------------
def auto_check_weather():

    print("🔄 Running automatic weather check...")

    for user in subscribers:
        city = user["city"]
        email = user["email"]

        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_KEY}"
        response = requests.get(url).json()

        if "list" not in response:
            continue

        warnings = []

        for item in response["list"]:
            harsh = detect_harsh_weather(item)
            if harsh:
                date = item["dt_txt"]
                warnings.append(f"{date}: {', '.join(harsh)}")

        if warnings:
            email_body = "🚨 HARSH WEATHER ALERT 🚨\n\n"
            email_body += "\n".join(warnings)
            email_body += "\n\nStay safe,\nCrop Advisory System"

            send_email(email, "⚠ Harsh Weather Alert!", email_body)

    print("✔ Automatic weather check completed.")


# ------------------------------------------------------
# START SCHEDULER
# ------------------------------------------------------
scheduler = BackgroundScheduler()

# Run every 24 hours
scheduler.add_job(auto_check_weather, "interval", seconds=2)

# You can also run every hour (optional):
# scheduler.add_job(auto_check_weather, "interval", hours=1)

scheduler.start()
print("⏳ Weather Scheduler Started (runs every 24 hours)")


@app.get("/")
def home():
    return {"message": "Weather Alert System Running (Auto-check enabled)"}
