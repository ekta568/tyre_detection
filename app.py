import streamlit as st
import requests
import os
import base64
from PIL import Image
from io import BytesIO

TOKEN = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

URL = (
    "https://bedrock-runtime.ap-south-1.amazonaws.com/"
    "model/global.anthropic.claude-sonnet-5/converse"
)


def detect_tyre_number(uploaded_file):
    image = Image.open(uploaded_file)

    # Convert phone image formats (HEIC etc.) to JPEG
    image = image.convert("RGB")

    # Reduce large phone images
    image.thumbnail((1600, 1600))

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=85)

    image_bytes = buffer.getvalue()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    image_format = "jpeg"

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {
                                "bytes": image_b64
                            }
                        }
                    },
                    {
                        "text": """
Extract the exact alphanumeric tyre serial number from the image. The serial number may start with "DOT" or may not start with "DOT". If it starts with "DOT", consider "DOT" as a prefix and return only the alphanumeric serial number that follows it, without including "DOT". If it does not start with "DOT", return the complete serial number exactly as shown. Do not hallucinate, infer, guess, or modify any characters. The complete serial number must be clearly readable and fully visible in the image. If any character is unclear, missing, obscured, or not fully visible, return exactly 'Improper Image'. No additional text.
"""
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }

    try:
        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        # Exact AWS Bedrock response
        result = response.json()["output"]["message"]["content"][0]["text"].strip()

        return result

    except Exception as e:
        return str(e)


# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(
    page_title="Tyre Serial Number Detection",
    layout="wide"
)

st.title("Tyre Serial Number Detection")

uploaded_file = st.file_uploader(
    "Upload Tyre Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.subheader("Tyre Image")
        st.image(Image.open(uploaded_file), use_container_width=True)

    with right:
        st.subheader("Detection")

        if st.button("Detect Serial Number", use_container_width=True):

            with st.spinner("Analyzing image..."):
                result = detect_tyre_number(uploaded_file)

            st.text_input(
                "Detected Serial Number",
                value=result,
                disabled=True
            )
