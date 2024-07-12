# Import necessary modules from FastAPI
from fastapi import FastAPI, Request, Depends
# Import CORS middleware to handle Cross-Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware
# Import BaseModel from Pydantic for data validation
from pydantic import BaseModel
# Import StreamingResponse for streaming responses
from fastapi.responses import StreamingResponse
# Import StaticFiles for serving static files
from fastapi.staticfiles import StaticFiles
# Import httpx for making HTTP requests (unused in this snippet)
import httpx
# Import os for interacting with the operating system (unused in this snippet)
import os
# Import asyncio for asynchronous programming (unused in this snippet)
import asyncio


# Import a custom function for generating model output
from utils import validate_api_key, get_model_output

# Initialize the FastAPI app
#app = FastAPI(dependencies=[Depends(validate_api_key)])
app = FastAPI()

# Add CORS middleware to the app to allow front-end to communicate with back-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize an empty list to store chat history
chat_history = []

# Define the message structure using Pydantic BaseModel
class Message(BaseModel):
    message: str  # Define a single field 'message' of type string

# Define an endpoint for handling chat messages
@app.post("/chat")
async def chat(message: Message, api_key: str = Depends(validate_api_key)):

    # Append the new message to the chat history
    chat_history.append({"role": "user", "content": message.message})

    # Create a StreamingResponse with the assistant's response using the chat history
    response = StreamingResponse(get_model_output(chat_history), media_type="text/event-stream")

    # Return the streaming response
    return response

# Mount the static directory to serve the HTML file
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Run the app using Uvicorn if the script is executed directly
if __name__ == '__main__':
    import uvicorn  # Import Uvicorn for running the app
    # Run the app on localhost at port 8000 with info log level
    #You can overwrite host and port e.g. using uvicorn chat_app:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level="info")

