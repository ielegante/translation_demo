from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from translate_demo import create_translator
from typing import Dict

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LLMConfig(BaseModel):
    model: str
    api_key: str

class TranslationRequest(BaseModel):
    text: str
    llm_config: LLMConfig

@app.post("/translate")
async def translate(request: TranslationRequest):
    print(request)
    try:
        translator = create_translator(
            model=request.llm_config.model,
            api_key=request.llm_config.api_key
        )
        result = translator.translate_text(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))