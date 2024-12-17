from fasthtml.common import *
import httpx
import os
import uvicorn

# Get backend URL from environment variable, default to local development URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

app, rt = fast_app(
    hdrs=(
        Script(src="https://cdn.tailwindcss.com"),
        Style("""
            body { background-color: #f3f4f6; }
            .container { max-width: 800px; margin: 2rem auto; }
            .card {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 2rem;
                margin-bottom: 1.5rem;
            }
            .loading { 
                opacity: 0.5; 
                pointer-events: none;
            }
            textarea { 
                min-height: 120px;
                width: 100%;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 0.75rem;
                margin: 0.5rem 0;
                font-size: 1rem;
            }
            .input-group {
                margin-bottom: 1.5rem;
            }
            .label {
                display: block;
                font-weight: 500;
                margin-bottom: 0.5rem;
                color: #374151;
            }
            select, input {
                width: 100%;
                padding: 0.5rem;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                margin-bottom: 1rem;
            }
            .btn {
                background-color: #2563eb;
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 6px;
                font-weight: 500;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .btn:hover {
                background-color: #1d4ed8;
            }
            .result-section {
                margin-top: 1.5rem;
                padding-top: 1.5rem;
                border-top: 1px solid #e5e7eb;
            }
            .result-title {
                font-weight: 600;
                color: #374151;
                margin-bottom: 0.5rem;
            }
            .result-content {
                margin-bottom: 1rem;
                line-height: 1.5;
            }
            .quality-pass {
                color: #059669;
                font-weight: 500;
            }
            .quality-fail {
                color: #dc2626;
                font-weight: 500;
            }
        """)
    )
)

@rt("/")
async def get():
    return Titled("English to Mandarin Translator",
        Container(
            Div(
                H1("English to Mandarin Translator", cls="text-2xl font-bold mb-6 text-gray-800"),
                
                # Model Configuration Card
                Div(
                    H2("Model Configuration", cls="text-xl font-semibold mb-4 text-gray-700"),
                    Div(
                        Div(
                            Label("Select Model:", cls="label"),
                            Select(
                                Option("Claude 3.5 Sonnet", value="claude-3-5-sonnet-20241022"),
                                Option("GPT-40", value="gpt-4o-2024-08-06"),
                                Option("Groq Llama 3.1 70b Versatile", value="llama-3.1-70b-versatile", selected=True),
                                Option("Gemini 2.0 Flash Exp", value="gemini-2.0-flash-exp-001"),
                                name="model",
                                id="model",
                            ),
                        ),
                        Div(
                            Label("API Key:", cls="label"),
                            Input(
                                type="password",
                                name="api_key",
                                id="api_key",
                                placeholder="Enter your API key here"
                            ),
                        ),
                        cls="input-group"
                    ),
                    cls="card"
                ),
                
                # Translation Card
                Div(
                    H2("Translation", cls="text-xl font-semibold mb-4 text-gray-700"),
                    Form(
                        Div(
                            Label("Enter English Text:", cls="label"),
                            Textarea(
                                id="text",
                                name="text",
                                placeholder="Type your English text here..."
                            ),
                            cls="input-group"
                        ),
                        Div(
                            Button("Translate", type="submit", cls="btn"),
                            cls="text-right"
                        ),
                        id="translate-form",
                        hx_post="/translate",
                        hx_target="#result",
                        hx_indicator=".loading",
                        hx_include="[name='model'],[name='api_key']"
                    ),
                    cls="card"
                ),
                
                # Results Card
                Div(
                    id="result",
                    cls="card"
                ),
                cls="container"
            )
        )
    )

async def call_translation_api(text: str, model: str, api_key: str) -> dict:
    """Make HTTP request to backend translation service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/translate",
                json={
                    "text": text,
                    "model_config": {
                        "model": model,
                        "api_key": api_key
                    }
                },
                timeout=30.0
            )
            if response.status_code != 200:
                return {
                    "error": f"Backend error: {response.text}"
                }
            return response.json()
    except httpx.RequestError as e:
        return {
            "error": f"Connection error: {str(e)}"
        }

@rt("/translate")
async def post(text: str, model: str, api_key: str):
    """Handle the translation request"""
    try:
        result = await call_translation_api(text, model, api_key)
        
        if "error" in result:
            return Div(
                P("Error occurred during translation", cls="text-red-600 font-medium"),
                P(result["error"], cls="text-red-500"),
                cls="p-4"
            )
            
        return Div(
            H3("Translation Results", cls="text-xl font-semibold mb-4 text-gray-700"),
            
            Div(
                Div(
                    P("Original Text", cls="result-title"),
                    P(result["original"], cls="result-content")
                ),
                
                Div(
                    P("Proofread English", cls="result-title"),
                    P(result["proofread_english"], cls="result-content")
                ),
                
                Div(
                    P("Mandarin Translation", cls="result-title"),
                    P(result["mandarin"], cls="result-content")
                ),
                
                Div(
                    P("Quality Check", cls="result-title"),
                    P(f"Grade: {result['quality_check']['grade']}", 
                      cls=f"result-content {'quality-pass' if result['quality_check']['grade'] == 'Pass' else 'quality-fail'}"),
                    P("Reasoning:", cls="font-medium mt-2"),
                    P(result['quality_check']['reasoning'], cls="result-content")
                ),
                cls="result-section"
            )
        )
    except Exception as e:
        return Div(
            P("Error occurred during translation", cls="text-red-600 font-medium"),
            P(str(e), cls="text-red-500"),
            cls="p-4"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )