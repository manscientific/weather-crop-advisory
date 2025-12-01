from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai import Client
import os
from dotenv import load_dotenv
import json
import base64

# Load ENV file
load_dotenv(override=True)

app = FastAPI()

# CORS configuration
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
    raise ValueError("❌ GEMINI_API_KEY not found in .env")

client = Client(api_key=API_KEY)


# -----------------------------------------------------------
# ------------- DATA MODELS ---------------------------------
# -----------------------------------------------------------

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


# -----------------------------------------------------------
# ------------- 1️⃣ CHATBOT ENDPOINT -------------------------
# -----------------------------------------------------------

conversation_history = []

@app.post("/api/chatbot")
async def chatbot(req: ChatRequest):

    user_message = req.message.strip()

    if not user_message:
        return {"reply": "Please enter a message."}

    conversation_history.append({"role": "user", "text": user_message})

    # Get last 6 messages for memory
    context = ""
    for msg in conversation_history[-6:]:
        speaker = "User" if msg["role"] == "user" else "Assistant"
        context += f"{speaker}: {msg['text']}\n"

    prompt = f"""
You are an agricultural assistant chatbot.
Keep responses short, friendly, and helpful.

Conversation so far:
{context}

User: {user_message}
Assistant:
"""

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        bot_reply = result.text.strip()

        conversation_history.append({"role": "assistant", "text": bot_reply})
        return {"reply": bot_reply}

    except Exception as e:
        print("Chatbot Error:", e)
        return {"reply": "AI is not responding. Try again later."}



# -----------------------------------------------------------
# ------------- 2️⃣ BASIC FERTILIZER/PESTICIDE ADVICE -------
# -----------------------------------------------------------

@app.post("/get-better-advice")
async def get_better_advice(req: BasicAdviceRequest):

    prompt = f"""
A farmer is growing {req.cropName}.
He plans to use:
- Fertilizer: {req.fertilizer}
- Pesticide: {req.pesticide}

Respond ONLY in clean JSON:

{{
  "better_fertilizer": "best alternative or 'None'",
  "fertilizer_reason": "simple hindi reasoning in 1-2 lines",

  "better_pesticide": "best alternative or 'None'",
  "pesticide_reason": "simple hindi reasoning in 1-2 lines"
}}
"""

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw = result.text.strip().replace("```json", "").replace("```", "")

        return json.loads(raw)

    except Exception as e:
        print("Basic Advice Error:", e)
        return {
            "better_fertilizer": "N/A",
            "fertilizer_reason": "Error occurred.",
            "better_pesticide": "N/A",
            "pesticide_reason": "Error occurred."
        }



# -----------------------------------------------------------
# ------------- 3️⃣ ECO-FRIENDLY ADVICE + SOIL REPORT -------
# -----------------------------------------------------------

@app.post("/get-environment-friendly-advice")
async def get_environment_friendly_advice(req: SoilAdviceRequest):

    prompt = f"""
You are an agricultural sustainability expert.

Soil Report:
- Nitrogen: {req.nitrogen}
- Phosphorus: {req.phosphorus}
- Potassium: {req.potassium}
- pH: {req.ph}
- Organic Carbon: {req.organic_carbon}%

Crop: {req.cropName}

Inputs farmer uses:
- Fertilizer: {req.fertilizer}
- Pesticide: {req.pesticide}

Return ONLY JSON:

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
        raw = result.text.strip().replace("```json", "").replace("```", "")
        return json.loads(raw)

    except Exception as e:
        print("Eco Advice Error:", e)
        return {
            "environment_friendly_fertilizer": "N/A",
            "fertilizer_reason": "AI failed.",
            "environment_friendly_pesticide": "N/A",
            "pesticide_reason": "AI failed.",
            "soil_health_advice": "Try again later."
        }



# -----------------------------------------------------------
# ------------- 4️⃣ LEAF DISEASE DETECTION -------------------
# -----------------------------------------------------------

@app.post("/detect-leaf-disease")
async def detect_leaf_disease(file: UploadFile = File(...)):

    image_bytes = await file.read()

    if len(image_bytes) > 6 * 1024 * 1024:  
        raise HTTPException(400, "Image too large (>6MB). Resize it.")

    # Convert to base64 data URI
    content_type = file.content_type or "image/jpeg"
    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:{content_type};base64,{b64_img}"

    prompt = f"""
You are a plant disease expert.

Analyze the leaf image below (base64 embedded).

Return ONLY JSON:

{{
  "disease_name": "",
  "severity": "",
  "cause": "",
  "chemical_treatment": "",
  "eco_friendly_solution": "",
  "prevention_tips": ""
}}

Image:
{data_uri}
"""

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw = result.text.strip().replace("```json", "").replace("```", "")

        try:
            return json.loads(raw)
        except:
            return {"error": "Could not parse JSON", "raw_output": raw}

    except Exception as e:
        print("Leaf Detection Error:", e)
        return {
            "disease_name": "N/A",
            "severity": "N/A",
            "cause": "AI failed to detect",
            "chemical_treatment": "N/A",
            "eco_friendly_solution": "N/A",
            "prevention_tips": "Try again later.",
            "debug_error": str(e)
        }



# -----------------------------------------------------------
# ------------- SERVER STARTER ------------------------------
# -----------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
