from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama

# Initialize FastAPI app
app = FastAPI()

# Define request model
class QueryRequest(BaseModel):
    message: str

# Define response model
class QueryResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    try:
        response = ollama.chat(
            model="deepseek-r1:1.5b",
            messages=[{"role": "user", "content": request.message}]
        )
        return {"reply": response["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "DeepSeek 1.5B API is running!"}
