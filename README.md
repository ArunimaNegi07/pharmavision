# PharmaVision

PharmaVision is a Streamlit-based prototype for prescription-image extraction and AI-assisted medication information.

## Features

- **Prescription reader:** Upload prescription images and request structured extraction of patient name, medicines, dosage, and notes.
- **Drug assistant:** Ask general medication-related questions about uses, side effects, and potential interactions.
- **Structured output:** The prescription reader uses a Pydantic schema and JSON parser to organize extracted information.

AI-generated results can contain errors. Handwritten prescriptions must be checked by a qualified pharmacist or healthcare professional. Do not use this prototype as the sole basis for treatment decisions.

## Tech Stack

- Python
- Streamlit
- Google Gemini API
- LangChain
- Pydantic

## Requirements

- Python 3.10 or later
- A Google Gemini API key
- Internet access for Gemini API requests

## Local Setup

Clone the repository:

```bash
git clone https://github.com/ArunimaNegi07/pharmavision.git
cd pharmavision
```

Create and activate a virtual environment.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Configure the API Key

On macOS or Linux, set the environment variable in your terminal. Replace the placeholder with your own key locally.

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

Alternatively, create `.streamlit/secrets.toml` locally:

```toml
google_api_key = "YOUR_API_KEY"
```

Never commit your actual API key or the secrets file. The repository's `.gitignore` excludes `.streamlit/secrets.toml`.

For deployment, configure the key through the hosting provider's secret settings.

The model can be overridden using the `GEMINI_MODEL` environment variable. The default is `gemini-2.5-flash`; confirm that this model is available to your Google API account.

## Run the Application

From the repository root:

```bash
streamlit run Home.py
```

Use Streamlit's navigation to open the prescription reader or drug assistant.

## List Available Gemini Models

After configuring `GOOGLE_API_KEY` or `GEMINI_API_KEY`, run:

```bash
python list_models.py
```

This utility lists models exposed by the configured API that support content generation.

## Current Limitations

- Prescription extraction depends on image quality and handwriting.
- Extracted medicine names and dosage instructions require human review.
- AI responses may be incomplete or inaccurate, or unavailable due to API errors, model access, network issues, or usage limits.
- The application has not been validated for clinical use.

## License

No license has been specified yet. Contact the repository owner before redistributing or reusing this project.
