"""Central config: loads env, builds shared clients, holds all constants.
Everything else in the project imports from here — single source of truth."""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

# Load .env FIRST — before anything tries to read a key.
load_dotenv()

# --- Constants (change them HERE, once, and the whole app follows) ---
# llama-3.1-8b-instant was shut down by Groq on 16 Aug 2026; this is Groq's
# recommended replacement (see console.groq.com/docs/deprecations).
GROQ_MODEL = "openai/gpt-oss-20b"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PERSIST_DIR = "data/chroma_db"        # the ONE Chroma path — never hardcode elsewhere
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- Shared clients, built ONCE and imported everywhere ---
llm = ChatGroq(model=GROQ_MODEL)      # reads GROQ_API_KEY from env automatically

# Same sentence-transformers model as before, but run through fastembed (ONNX)
# instead of torch — a much smaller install, which is what free hosting needs.
embeddings = FastEmbedEmbeddings(model_name=EMBED_MODEL)