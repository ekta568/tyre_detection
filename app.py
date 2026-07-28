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

    if file_extension == "png":
        image_format = "png"
    else:
        image_format = "jpeg"

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
Return and extract exact alphanumeric tyre serial number from the image. If unable to identify then return 'Improper Image'. No additional text.
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
            timeout=120
        )

        if response.status_code == 401:
            return "Authentication failed. Please try again later."

        elif response.status_code == 400:
            return "Unable to process the uploaded image. Please try another image."

        elif response.status_code == 408:
            return "The request timed out. Please try again."

        elif response.status_code in [429, 500, 502, 503, 504]:
            return "Detection service is temporarily unavailable. Please try again later."

        elif response.status_code != 200:
            return "An unexpected error occurred. Please try again later."

        data = response.json()

        try:
            result = data["output"]["message"]["content"][-1]["text"].strip()

            if result.lower() == "improper image":
                return "Improper Image"

            return result

        except (KeyError, IndexError, TypeError):
            return "Received an invalid response from the detection service."

    except requests.exceptions.Timeout:
        return "The request timed out. Please try again."

    except requests.exceptions.ConnectionError:
        return "Unable to connect to the detection service. Please try again later."

    except requests.exceptions.RequestException:
        return "An unexpected error occurred. Please try again later."

    except Exception:
        return "An unexpected error occurred. Please try again later."


# STREAMLIT UI
st.set_page_config(
    page_title="Tyre Serial Number Detection",
    layout="wide"
)

st.title("Tyre Serial Number Detection")

uploaded_file = st.file_uploader(
    "Upload Tyre Image",
    type=[ "jpeg", "png"]
)

if uploaded_file:

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.subheader("Tyre Image")

        st.image(
            uploaded_file,
            use_container_width=True
        )

    with right:
        st.subheader("Detection")

        if st.button("Detect Serial Number", use_container_width=True):

            with st.spinner("Analyzing image..."):
                result = detect_tyre_number(uploaded_file)

            st.success("Completed")

            st.text_input(
                "Detected Serial Number",
                value=result,
                disabled=True
            )
