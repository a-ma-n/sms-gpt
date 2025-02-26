from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
from deep_translator import GoogleTranslator
from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
import langdetect

app = FastAPI()

# Request model with an extra field for target language
class QueryRequest(BaseModel):
    message: str
    target_language: str  # Accepts "english", "hindi", "hinglish", or "all"

# Response model for "all" option (optional fields)
class QueryResponse(BaseModel):
    reply_english: str = None
    reply_hindi: str = None
    reply_hinglish: str = None
    reply: str = None  # for a single reply response

def detect_language(text: str) -> str:
    try:
        return langdetect.detect(text[:100])
    except Exception:
        return "unknown"

def to_english(text: str, source: str = "hi") -> str:
    """Translate text from a source language (default Hindi) to English."""
    return GoogleTranslator(source=source, target='en').translate(text)

def english_to_hindi(english_text: str) -> str:
    """Translate English text to Hindi."""
    return GoogleTranslator(source='en', target='hi').translate(english_text)

def hindi_to_hinglish(hindi_text: str) -> str:
    """Transliterate Hindi (Devanagari) to Latin (Hinglish) using ITRANS."""
    return transliterate(hindi_text, DEVANAGARI, ITRANS)

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    try:
        user_text = request.message.strip()
        target = request.target_language.lower().strip()
        detected_lang = detect_language(user_text)

        # If input is English, use it directly; otherwise assume Hindi/Hinglish.
        if detected_lang == "en":
            query = user_text
        else:
            query = to_english(user_text, source="hi")

        # Query the LLM (DeepSeek 1.5B via Ollama)
        response = ollama.chat(
            model="deepseek-r1:1.5b",
            messages=[{"role": "user", "content": query}]
        )
        ai_reply_english = response["message"]["content"]

        # Convert the LLM's English reply to Hindi and then to Hinglish.
        ai_reply_hindi = english_to_hindi(ai_reply_english)
        ai_reply_hinglish = hindi_to_hinglish(ai_reply_hindi)

        # Wrap each response in <think> tags.
        formatted_english = f"{ai_reply_english}"
        formatted_hindi = f"{ai_reply_hindi}"
        formatted_hinglish = f"{ai_reply_hinglish}"

        # Return based on the target language requested.
        if target == "english":
            return {"reply": formatted_english}
        elif target == "hindi":
            return {"reply": formatted_hindi}
        elif target == "hinglish":
            return {"reply": formatted_hinglish}
        elif target == "all":
            return {
                "reply_english": formatted_english,
                "reply_hindi": formatted_hindi,
                "reply_hinglish": formatted_hinglish,
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported target language. Use english, hindi, hinglish, or all."
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "DeepSeek 1.5B API is running!"}
