"""streamlit_app.py — entry point for Streamlit Community Cloud.

Locally the project runs as TWO programs: the FastAPI backend (:8000) and
the Streamlit UI (:8501). Streamlit Cloud starts only ONE program, so this
file starts the FastAPI backend in a background thread inside the same
container, waits until it answers /ping, then runs the normal UI.

ui/app.py is unchanged and still talks to the API over HTTP only.

Run locally (one command instead of two):  streamlit run streamlit_app.py
"""

import os
import runpy
import sys
import threading
import time

import requests
import streamlit as st
import uvicorn

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)                      # all "data/..." paths are relative to the repo root
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)        # so uvicorn can import api.main

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Studybook", layout="wide")


def load_secrets_into_env():
    """Streamlit Cloud keeps keys (like GROQ_API_KEY) in st.secrets. The backend
    reads them from environment variables, so copy them over BEFORE it starts."""
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str):
                os.environ.setdefault(key, value)
    except Exception:
        pass  # no secrets file locally — the .env file is used instead


@st.cache_resource(show_spinner="Starting the backend — first load can take a minute...")
def start_backend():
    """Runs ONCE per server (cache_resource), not on every Streamlit re-run."""
    os.makedirs("data", exist_ok=True)

    if not os.environ.get("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is missing. Add it under Manage app → Settings → Secrets.")
        st.stop()

    config = uvicorn.Config("api.main:api", host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for the API. The first start downloads the embedding model, so be patient.
    for _ in range(300):
        if not thread.is_alive():
            raise RuntimeError("Backend crashed while starting — see the error above in the logs.")
        try:
            if requests.get(f"{API_URL}/ping", timeout=2).ok:
                return server
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    raise RuntimeError("Backend did not start within 5 minutes — check the app logs.")


load_secrets_into_env()


start_backend()

# Hand over to the normal UI file, exactly as before.
runpy.run_path(os.path.join(ROOT, "ui", "app.py"), run_name="__main__")
