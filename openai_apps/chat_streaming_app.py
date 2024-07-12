from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os
import asyncio
import json

# Initialize the FastAPI app
app = FastAPI()

# CORS middleware to allow front-end to communicate with back-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-3.5-turbo"

async def get_model_output(message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": message,
        "max_tokens": 1000,
        "stream": True
    }

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, headers=headers, json=data) as response:
            buffer = ""
            async for chunk in response.aiter_text():
                buffer += chunk
                lines = buffer.splitlines()
                for line in lines[:-1]:  # Process all lines except the last incomplete one
                    if line.startswith("data:"):
                        data_str = line.removeprefix("data: ").strip()
                        if data_str and data_str != "[DONE]":
                            try:
                                data_json = json.loads(data_str)
                                if 'choices' in data_json and data_json['choices']:
                                    delta_content = data_json['choices'][0]['delta'].get('content', '')
                                    if delta_content:
                                        yield delta_content
                            except json.JSONDecodeError as e:
                                print(f"JSON decoding error: {e}")
                buffer = lines[-1]  # Keep the last incomplete line in the buffer

# Store chat history
chat_history = []

# Define the message structure
class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(message: Message):
    # Append the new message to the chat history
    chat_history.append({"role": "user", "content": message.message})

    # Create a StreamingResponse with the assistant's response
    response = StreamingResponse(get_model_output(chat_history), media_type="text/event-stream")

    return response

# Mount the static directory to serve the HTML file
app.mount("/", StaticFiles(directory="static_stream", html=True), name="static_stream")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level="info")
