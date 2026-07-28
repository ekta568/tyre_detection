import requests
import base64
from prompt import TYRE_PROMPT

API_KEY = "AWS_BEARER_TOKEN_BEDROCK"

MODEL_ID = "anthropic.claude-sonnet-5"

def detect_tyre_number(image_bytes):

    image_base64 = base64.b64encode(
        image_bytes
    ).decode()

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": TYRE_PROMPT
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://bedrock-runtime.ap-south-1.amazonaws.com/model/global.anthropic.claude-sonnet-5/converse",
        headers=headers,
        json=payload
    )

    return response.json()