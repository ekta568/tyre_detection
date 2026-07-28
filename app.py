import streamlit as st
import requests
import os
import base64

TOKEN = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

URL = (
    "https://bedrock-runtime.ap-south-1.amazonaws.com/"
    "model/global.anthropic.claude-sonnet-5/converse"
)


def detect_tyre_number(uploaded_file):
    image_bytes = uploaded_file.getvalue()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    file_extension = uploaded_file.name.split(".")[-1].lower()

    image_format = {
        "png": "png",
        "jpg": "jpeg",
        "jpeg": "jpeg",
    }.get(file_extension)

    if image_format is None:
        return "ERROR: Unsupported image format"

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": image_format,
                            "source": {
                                "bytes": image_b64
                            }
                        }
                    },
                    {
                        "text": """
Return and extract exact alphanumeric tyre serial number from the image.
If unable to identify then return 'Improper Image'.
No additional text.
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
        result = response.text

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
        st.image(uploaded_file, use_container_width=True)

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
