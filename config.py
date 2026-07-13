"""Central config: loads env, builds shared clients, holds all constants.
Everything else in the project imports from here — single source of truth."""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# Load .env FIRST — before anything tries to read a key.
load_dotenv()

# --- Constants (change them HERE, once, and the whole app follows) ---
GROQ_MODEL = "llama-3.1-8b-instant"
EMBED_MODEL = "all-MiniLM-L6-v2"
PERSIST_DIR = "data/chroma_db"        # the ONE Chroma path — never hardcode elsewhere
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- Shared clients, built ONCE and imported everywhere ---
llm = ChatGroq(model=GROQ_MODEL)      # reads GROQ_API_KEY from env automatically

embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)