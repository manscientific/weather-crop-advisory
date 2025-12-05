from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai import Client
import os
from dotenv import load_dotenv
import json
import base64

# Load ENV
load_dotenv(override=True)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Gemini Client
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing in .env")

client = Client(api_key=API_KEY)


# -------------------------------------------------------------------
# Small middleware to avoid body-size issues on Railway / Render
# -------------------------------------------------------------------
@app.middleware("http")
async def body_size_patch(request: Request, call_next):
    request._receive = request._receive
    return await call_next(request)


# -------------------------------------------------------------------
# DATA MODELS
# -------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str

class BasicAdviceRequest(BaseModel):
    cropName: str
    fertilizer: str
    pesticide: str

class SoilAdviceRequest(BaseModel):
    cropName: str
    fertilizer: str
    pesticide: str
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    organic_carbon: float


# -------------------------------------------------------------------
# 1️⃣ CHATBOT
# -------------------------------------------------------------------

conversation_history = []

@app.post("/api/chatbot")
async def chatbot(req: ChatRequest):
    user_message = req.message.strip()
    if not user_message:
        return {"reply": "Please enter a message."}

    conversation_history.append({"role": "user", "text": user_message})

    # Last 6 messages only
    context = "\n".join(
        [("User" if m["role"] == "user" else "Assistant") + ": " + m["text"]
         for m in conversation_history[-6:]]
    )

    prompt = f"""
You are an agricultural assistant.
Keep responses short and helpful.

Conversation:
{context}

User: {user_message}
Assistant:
"""

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        reply = result.text.strip()

        conversation_history.append({"role": "assistant", "text": reply})
        return {"reply": reply}

    except Exception as e:
        print("Chatbot Error:", e)
        return {"reply": "AI error occurred. Try again later."}


# -------------------------------------------------------------------
# 2️⃣ BASIC ADVICE
# -------------------------------------------------------------------

@app.post("/get-better-advice")
async def get_better_advice(req: BasicAdviceRequest):

    prompt = f"""
Suggest better fertilizer & pesticide for {req.cropName}.

Inputs:
- Fertilizer: {req.fertilizer}
- Pesticide: {req.pesticide}

Return ONLY JSON:
{{
  "better_fertilizer": "",
  "fertilizer_reason": "",
  "better_pesticide": "",
  "pesticide_reason": ""
}}
"""

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = result.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    except Exception as e:
        print("Advice Error:", e)
        return {
            "better_fertilizer": "N/A",
            "fertilizer_reason": "AI failed.",
            "better_pesticide": "N/A",
            "pesticide_reason": "AI failed."
        }


# -------------------------------------------------------------------
# 3️⃣ ECO & SOIL HEALTH ADVICE
# -------------------------------------------------------------------

@app.post("/get-environment-friendly-advice")
async def get_environment_friendly_advice(req: SoilAdviceRequest):

    prompt = f"""
You are an agricultural sustainability expert.
Respond ONLY in this language: {req.language}

Soil:
N={req.nitrogen}, P={req.phosphorus}, K={req.potassium}, pH={req.ph},
Organic Carbon={req.organic_carbon}%

Crop: {req.cropName}

Inputs:
Fertilizer={req.fertilizer}
Pesticide={req.pesticide}

Return ONLY JSON in the selected language:
{{
  "environment_friendly_fertilizer": "",
  "fertilizer_reason": "",
  "environment_friendly_pesticide": "",
  "pesticide_reason": "",
  "soil_health_advice": ""
}}
"""

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = result.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    except Exception as e:
        print("Soil Advice Error:", e)
        return {
            "environment_friendly_fertilizer": "N/A",
            "fertilizer_reason": "AI failed.",
            "environment_friendly_pesticide": "N/A",
            "pesticide_reason": "AI failed.",
            "soil_health_advice": "Try again later."
        }


# -------------------------------------------------------------------
# 4️⃣ LEAF DISEASE DETECTION (FIXED)
# -------------------------------------------------------------------

@app.post("/detect-leaf-disease")
async def detect_leaf_disease(file: UploadFile = File(...)):

    image_bytes = await file.read()

    if len(image_bytes) > 6 * 1024 * 1024:
        raise HTTPException(400, "Image too large (>6MB).")

    # Convert to base64 but DO NOT embed in text
    b64_img = base64.b64encode(image_bytes).decode()
    mime = file.content_type or "image/jpeg"

    prompt = """
Identify the leaf disease and return ONLY JSON:

{
 "disease_name": "",
 "severity": "",
 "cause": "",
 "chemical_treatment": "",
 "eco_friendly_solution": "",
 "prevention_tips": ""
}
"""

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime,
                        "data": b64_img
                    }
                }
            ]
        )

        text = result.text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        print("Leaf Error:", e)
        return {
            "disease_name": "N/A",
            "severity": "N/A",
            "cause": "Processing failed",
            "chemical_treatment": "N/A",
            "eco_friendly_solution": "N/A",
            "prevention_tips": "Try again later.",
            "debug_error": str(e)
        }


# -------------------------------------------------------------------
# RUN SERVER
# -------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
