# Import requests for making HTTP requests
import requests
# Import json for JSON manipulation
import json

from fastapi import Header, HTTPException

# Specify the model to be used
model = "llama3_supermario"  # Update this for whatever model you wish to use

API_KEY = 'gaQ2ooNrlgnEHow-_f3-bfjyerinvZUWENERwBbOgv8ZZsT4UficbtvY0DHXp92xHkk'


# Define an asynchronous function to get model output
async def get_model_output(messages):
    # Make a POST request to the chat API with the model and messages
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",  # API endpoint for chat
        json={"model": model, "messages": messages, "stream": True},  # Payload with model and messages
        stream=True  # Enable streaming response
    )

    # Raise an error if the request was unsuccessful
    r.raise_for_status()
    
    # Initialize an empty string to store the output
    output = ""

    # Iterate over each line in the streaming response
    for line in r.iter_lines():
        # Parse the line as JSON
        body = json.loads(line)
        # If there's an error in the response, raise an exception
        if "error" in body:
            raise Exception(body["error"])
        # If the response indicates that streaming is not done
        if body.get("done") is False:
            # Get the message content
            message = body.get("message", "")
            content = message.get("content", "")
            # Append the content to the output string
            output += content
            # Yield the content as it's received
            yield content



# Define a function to validate the API key from the header
def validate_api_key(api_key: str = Header(...)):
    """
    Dependency to extract and validate the API key from the request header.
    """
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return api_key


def get_api_key(api_key: str = Header(...)):
    """
    Dependency to extract and validate the API key from the request header.
    """
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return api_key


def is_valid_api_key(api_key):

    if api_key is None:
        raise HTTPException(status_code=401, detail="No API key provided")

    if api_key == API_KEY:
        return True
    else:
        raise HTTPException(status_code=403, detail="Invalid  API key")


