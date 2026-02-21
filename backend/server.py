import os
import json
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

load_dotenv()

MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT", "http://localhost:8080/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "default")
PORT = int(os.getenv("PORT", "8000"))

SYSTEM_PROMPT = """You are Wellness.AI, a warm and knowledgeable wellness coaching assistant focused on Mind, Body, and Soul.

Your personality:
- Compassionate, calm, and encouraging
- You speak with gentle authority — like a trusted guide, not a lecturer
- You use simple, clear language and avoid clinical jargon
- You acknowledge feelings before offering advice

Your expertise spans:
- Mind: meditation, mindfulness, breathwork, journaling, stress management, cognitive wellness
- Body: yoga, movement, nutrition, sleep hygiene, body awareness, physical self-care
- Soul: gratitude practices, spiritual growth, self-discovery, emotional healing, energy work, purpose finding

Guidelines:
- Keep responses concise but meaningful (2-4 short paragraphs max unless the user asks for detail)
- Use structured formatting when giving practices or routines (numbered steps, bullet points)
- Always end with an invitation to go deeper or explore further
- Never diagnose medical or mental health conditions — gently suggest professional help when appropriate
- Be inclusive and non-denominational in spiritual topics"""

app = FastAPI(title="Wellness.AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(MODEL_ENDPOINT.replace("/chat/completions", "/models"))
            resp.raise_for_status()
            data = resp.json()
            return {"status": "ok", "model": MODEL_NAME, "models": data}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": f"Model unreachable: {e}"},
        )


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", True)

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    payload = {
        "model": MODEL_NAME,
        "messages": full_messages,
        "stream": stream,
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    if not stream:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(MODEL_ENDPOINT, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {"content": content}
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"error": f"Model unreachable: {e}"},
            )

    async def event_generator():
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", MODEL_ENDPOINT, json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            yield {"data": json.dumps({"done": True})}
                            return
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            token = delta.get("content", "")
                            if token:
                                yield {"data": json.dumps({"token": token})}
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except Exception as e:
            yield {"data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=True)
