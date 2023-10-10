from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI(debug=True)
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": ""})

@app.post("/Summarize")
async def summarize(request: Request, data: str = Form(...), maxL: int = Form(...)):
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {'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'}"}

        minL = maxL // 4

        async with httpx.AsyncClient(timeout=500.0) as client:
            response = await client.post(
                API_URL,
                headers=headers,
                json={"inputs": data, "parameters": {"min_length": minL, "max_length": maxL}},
            )

        if response.status_code == 200:
            try:
                output = response.json()
                if isinstance(output, list) and len(output) > 0:
                    summary_text = output[0].get("summary_text", "Summary not found in response")
                else:
                    summary_text = "Empty response from the API"
            except (ValueError, KeyError):
                summary_text = "Error processing response"
        else:
            summary_text = f"API request failed with status code: {response.status_code}"

    except httpx.RequestError as e:
        summary_text = f"HTTP request error: {str(e)}"

    return templates.TemplateResponse("index.html", {"request": request, "result": summary_text})
