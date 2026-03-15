"""
Grok API Server - Improved & Clean Version
Based on: https://github.com/realasfngl/Grok-Api
Improvements: CORS support, better error handling, health check, cleaner code
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from core import Grok

app = FastAPI(
    title="Grok API Wrapper",
    description="Free Grok API wrapper - no account needed",
    version="1.0.0"
)

# Allow all origins so the web UI can connect from any host
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    message: str
    model: Optional[str] = "grok-3-fast"
    proxy: Optional[str] = None
    extra_data: Optional[dict] = None


class AskResponse(BaseModel):
    status: str
    response: str
    stream_response: list
    images: Optional[list]
    extra_data: Optional[dict]


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Grok API Wrapper is running",
        "endpoints": ["/ask", "/health", "/models"]
    }


@app.get("/health")
def health():
    """Health check endpoint for Railway / uptime monitors"""
    return {"status": "ok"}


@app.get("/models")
def models():
    """List available Grok models"""
    return {
        "models": [
            {"id": "grok-3-auto",               "description": "Automatic mode"},
            {"id": "grok-3-fast",               "description": "Fast processing (recommended)"},
            {"id": "grok-4",                    "description": "Expert mode"},
            {"id": "grok-4-mini-thinking-tahoe","description": "Mini thinking mode"},
        ]
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """
    Send a message to Grok.
    - First message: leave extra_data as null
    - Follow-up messages: pass the extra_data returned from the previous response
    """
    try:
        grok = Grok(req.model, req.proxy)
        result = grok.start_convo(req.message, extra_data=req.extra_data)
        return {
            "status": "success",
            "response": result.get("response", ""),
            "stream_response": result.get("stream_response", []),
            "images": result.get("images"),
            "extra_data": result.get("extra_data"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=int(__import__("os").environ.get("PORT", 6969)),
        workers=4,
        log_level="info"
    )
