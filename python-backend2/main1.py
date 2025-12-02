from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import sib_api_v3_sdk

load_dotenv()

app = FastAPI()

# -------------------------------------------------------
# CORS (FIXED)
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# ENV VARIABLES
# -------------------------------------------------------
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER")   # Example: yourgmail@gmail.com
BREVO_SENDER_NAME = os.getenv("BREVO_NAME", "Crop Advisory System")

# -------------------------------------------------------
# BREVO CLIENT SETUP
# -------------------------------------------------------
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = BREVO_API_KEY
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)

# In-memory subscriber list
subscribers = []

# -------------------------------------------------------
# MODEL
# -------------------------------------------------------
class EmailRequest(BaseModel):
    email: str
    city: str = "Delhi"


# -------------------------------------------------------
# SUBSCRIBE ENDPOINT
# -------------------------------------------------------
@app.post("/subscribe-weather-alert")
def subscribe(req: EmailRequest):
    subscribers.append({"email": req.email, "city": req.city})
    return {"message": "Subscription successful!"}


# -------------------------------------------------------
# SEND EMAIL USING BREVO
# -------------------------------------------------------
def send_email(to_email, subject, body):

    email_content = sib_api_v3_sdk.SendSmtpEmail(
        sender={"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL},
        to=[{"email": to_email}],
        subject=subject,
        html_content=body,
    )

    try:
        response = api_instance.send_transac_email(email_content)
        print(f"📨 Email sent to {to_email} | Message ID: {response.message_id}")
    except Exception as e:
        print("❌ Brevo Error:", str(e))


# -------------------------------------------------------
# HARSH WEATHER DETECTION LOGIC
# -------------------------------------------------------
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
        alerts.append("⛈ Storm")
    if "snow" in condition:
        alerts.append("❄ Snowfall")

    return alerts


# -------------------------------------------------------
# AUTO WEATHER CHECKER
# -------------------------------------------------------
def auto_check_weather():

    print("🔄 Running automatic weather check...")

    for user in subscribers:
        city = user["city"]
        email = user["email"]

        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_KEY}"
        response = requests.get(url).json()

        if "list" not in response:
            print(f"⚠ Failed to fetch weather for {city}")
            continue

        warnings = []

        for item in response["list"]:
            harsh = detect_harsh_weather(item)
            if harsh:
                warnings.append(f"{item['dt_txt']}: {', '.join(harsh)}")

        if warnings:
            body = (
                "🚨 <b>Harsh Weather Alert</b> 🚨<br><br>"
                + "<br>".join(warnings)
                + "<br><br>Stay safe,<br><b>Crop Advisory System</b>"
            )

            send_email(email, "⚠ Harsh Weather Alert!", body)

    print("✔ Automatic weather check completed.")


# -------------------------------------------------------
# BACKGROUND SCHEDULER
# -------------------------------------------------------
scheduler = BackgroundScheduler()

# Change seconds=2 for testing; hours=24 in production
scheduler.add_job(auto_check_weather, "interval", seconds=2)

scheduler.start()
print("⏳ Weather Scheduler Started")


# -------------------------------------------------------
# HOME ROUTE
# -------------------------------------------------------
@app.get("/")
def home():
    return {"message": "Weather Alert System (Brevo Version) Running!"}
