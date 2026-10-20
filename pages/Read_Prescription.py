import os
import base64
import json
from typing import List, Dict
from pydantic import BaseModel
import streamlit as st
import tempfile

# --- CORRECTED LANGCHAIN IMPORTS ---
# ChatOpenAI is now in langchain_openai
from langchain_google_genai import ChatGoogleGenerativeAI
# HumanMessage and other message types are in langchain_core.messages
from langchain_core.messages import HumanMessage
# JsonOutputParser is now in langchain_core.output_parsers
from langchain_core.output_parsers import JsonOutputParser
# Import for general exceptions
from langchain_core.exceptions import OutputParserException


# --- 1. Pydantic Model Definition ---
class PrescriptionInformations(BaseModel):
    """Defines the structure for extracted prescription data."""
    patient_name: str
    medicines: List[str]
    dosage: str
    notes: str

# --- 2. Helper Functions ---

def load_images(inputs: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Load images from given file paths and convert to base64 strings.
    """
    image_paths = inputs.get("image_paths", [])
    images_base64 = []

    for path in image_paths:
        try:
            with open(path, "rb") as image_file:
                # Determine image type for the base64 URL
                extension = os.path.splitext(path)[1].lower()
                mime_type = "image/jpeg" if extension in ['.jpg', '.jpeg'] else "image/png"

                encoded = base64.b64encode(image_file.read()).decode("utf-8")
                images_base64.append((encoded, mime_type))
        except FileNotFoundError:
            st.error(f"Error: Internal file not found at {path}")
            pass

    # Returns a list of tuples: (base64_string, mime_type)
    return {"images": images_base64}

def image_model(images_data: List[tuple], parser: JsonOutputParser) -> str:
    """Run Gemini to extract structured information from prescription images."""
    # Load the key from Streamlit secrets or environment variables.
    try:
        api_key = (
            st.secrets.get("google_api_key")
            or st.secrets.get("GEMINI_API_KEY")
        )
    except Exception:
        api_key = None

    api_key = (
        api_key
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
    )

    if not api_key:
        return (
            "Error: Configure google_api_key in Streamlit secrets "
            "or set the GOOGLE_API_KEY environment variable."
        )

    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    model = ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model=model_name,
        temperature=0.0,
    )

    # Construct the image_url objects for the multimodal message
    image_url_parts = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{img_str}"}
        }
        for img_str, mime_type in images_data
    ]

    # The prompt contains text instructions, including the format instructions
    text_prompt = f"""
You are a highly accurate AI assistant specializing in interpreting handwritten medical prescriptions.
You are given one or more images of medical prescriptions.
Extract the prescription information with details like patient name, a list of medicines, dosage instructions, and any general notes or doctor's comments.

Output the data strictly in this JSON format:
{parser.get_format_instructions()}
""".strip()

    # The content list sends the text prompt AND the image parts
    messages = [
        HumanMessage(
            content=[
                {"type": "text", "text": text_prompt},
                *image_url_parts
            ]
        )
    ]

    # Call the model using .invoke()
    try:
        msg = model.invoke(messages)
        content = msg.content
        if isinstance(content, list):
            content = ''.join(c.get('text', '') if isinstance(c, dict) else str(c) for c in content)
        return content
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return ""


# --- 3. Main Logic Function ---

def get_prescription_informations(image_paths: List[str]) -> dict:
    """
    High-level function to load images, call the model, and parse output.
    """
    parser = JsonOutputParser(pydantic_object=PrescriptionInformations)

    # 1. Load images
    images_dict = load_images({"image_paths": image_paths})

    if not images_dict.get('images'):
        # Note: If this returns an error, it means st.secrets failed, which is handled in image_model
        return {"error": "No images loaded."}

    # 2. Call image_model
    model_output = image_model(images_dict['images'], parser)

    if not model_output or "Error" in model_output:
        return {"error": model_output if "Error" in model_output else "Model returned empty output."}

    # 3. Parse the model output JSON string
    try:
        parsed = parser.parse(model_output)
        return parsed

    except OutputParserException as e:
        st.error("Model did not return valid JSON format.")
        st.code(model_output, language='json')
        return {"error": "Failed to parse model output into required JSON format."}


# --- 4. Streamlit App Entry Point ---

def main():
    st.set_page_config(page_title="PharmaVision", layout="centered")
    st.title("💊 PharmaVision: Prescription Extractor")
    st.subheader("Upload an image of a prescription below.")

    # Use st.file_uploader to let the user select a file
    uploaded_file = st.file_uploader(
        "Choose a prescription image (JPG or PNG)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        # 1. Display the uploaded image
        st.image(uploaded_file, caption='Uploaded Prescription', width='stretch')

        # 2. Save the UploadedFile object to a temporary file on disk
        try:
            # Use tempfile to create a path for your load_images function
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                image_path = tmp_file.name

            # 3. Process the file
            with st.spinner('Extracting and analyzing information...'):
                final_result = get_prescription_informations([image_path])

            # 4. Display Results
            if "error" in final_result:
                st.error(f"Processing failed: {final_result['error']}")
            else:
                st.success("Extraction Complete!")

                # Display the structured output as a table and interactive JSON
                st.markdown("### Extracted Details")

                # Create a simple display table
                data_for_table = [
                    {"Field": "Patient Name", "Value": final_result.get("patient_name", "N/A")},
                    {"Field": "Dosage Notes", "Value": final_result.get("dosage", "N/A")},
                    {"Field": "General Notes", "Value": final_result.get("notes", "N/A")},
                ]
                st.table(data_for_table)

                st.markdown("### Prescribed Medicines")
                # Handle medicine list nicely
                if final_result.get("medicines"):
                    st.code('\n'.join(final_result['medicines']), language='text')
                else:
                    st.warning("No medicines were clearly identified.")

                # Display the raw JSON response
                st.markdown("---")
                st.markdown("### Full JSON Output")
                st.json(final_result, expanded=False)

        except Exception as e:
            st.error(f"An unexpected error occurred during file saving or processing: {e}")
            st.info("Please ensure your .streamlit/secrets.toml file is configured correctly.")

        finally:
            # 5. Clean up the temporary file
            if 'image_path' in locals() and os.path.exists(image_path):
                os.unlink(image_path)


if __name__ == "__main__":
    main()
