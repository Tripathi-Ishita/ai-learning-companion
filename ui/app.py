"""ui/app.py — Studybook frontend.

Talks to the API over HTTP only. Imports nothing from this project.
Run:  streamlit run ui/app.py    (API must be running on :8000)
"""

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


st.set_page_config(page_title="Studybook", layout="wide")

# --- state that must survive a re-run ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []
if "chunks_indexed" not in st.session_state:
    st.session_state.chunks_indexed = 0
if "handled" not in st.session_state:
    st.session_state.handled = set()

# --- sidebar ---

# ---------------- helper: shorten long names for the SOURCES list ----------------
def short(name: str, limit: int = 34) -> str:
    """The mockup truncates long source names with an ellipsis.
    'Stanford CS224N — Lecture 8: Attention...' instead of the full URL."""
    return name if len(name) <= limit else name[:limit] + "..."


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("Studybook")
    st.caption("Ask questions against your own material.")

    # ---------- upload a document ----------
    st.subheader("Upload a document")

    uploaded = st.file_uploader("Drag and drop file here", type=["pdf", "txt"])

    # THE GUARD: file_uploader returns the SAME file on every re-run,
    # so without checking `handled` we would re-upload it on every click.
    if uploaded is not None and uploaded.name not in st.session_state.handled:
        with st.spinner(f"Indexing {uploaded.name}..."):
            r = requests.post(
                f"{API_URL}/upload",
                files={"file": (uploaded.name, uploaded.getvalue())},
            )
        data = r.json()
        if data.get("ok"):
            badge = "PDF" if uploaded.name.lower().endswith(".pdf") else "TXT"
            st.session_state.sources.append((badge, uploaded.name))
            st.session_state.chunks_indexed += data["chunks_added"]
            st.session_state.handled.add(uploaded.name)
            st.success(f"{data['chunks_added']} chunks indexed")
        else:
            st.error("Could not index that file.")

    # ---------- add a link ----------
    st.subheader("Add a link")

    # st.form groups widgets so NOTHING happens until the submit button is pressed.
    # This is what kills the "Press Enter to apply" hint — inside a form,
    # typing doesn't need to be "applied", because the form submit does it.
    with st.form("add_link_form", clear_on_submit=True):
        url = st.text_input(
            "url",
            label_visibility="collapsed",     # hide the label, keep it for screen readers
            placeholder="Web page or YouTube URL",
        )
        # inside a form you MUST use form_submit_button, not st.button
        submitted = st.form_submit_button(
            "Add", type="primary", use_container_width=True
        )

    if submitted and url:
        with st.spinner("Indexing..."):
            r = requests.post(f"{API_URL}/upload", data={"url": url})
        data = r.json()
        if data.get("ok"):
            badge = "YT" if ("youtube.com" in url or "youtu.be" in url) else "WEB"
            st.session_state.sources.append((badge, url))
            st.session_state.chunks_indexed += data["chunks_added"]
            st.success(f"{data['chunks_added']} chunks indexed")
        else:
            st.error("Could not index that link.")

    # ---------- SOURCES list ----------
    st.divider()
    st.markdown("**SOURCES**")

    if not st.session_state.sources:
        st.caption("No sources yet.")          # the mockup's empty state
    else:
        for badge, name in st.session_state.sources:
            # two columns: a narrow one for the badge, a wide one for the name
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f"`{badge}`")      # backticks render a grey pill
            with c2:
                st.markdown(short(name))

    # ---------- footer ----------
    st.divider()
    n = len(st.session_state.sources)
    st.caption(f"{st.session_state.chunks_indexed} chunks indexed across {n} sources")

    # user id — not in the mockup, kept small and last so it doesn't compete
    USER_ID = st.text_input("User", value="ishita")

    

# ---------------- MAIN PANE ----------------

st.title("Studybook")

# f-string recomputed on EVERY re-run, which is why it self-updates
st.caption(
    f"{len(st.session_state.sources)} sources · "
    f"{st.session_state.chunks_indexed} chunks indexed"
)

st.divider()

# ---------- empty state (mockup 1c / 1d) ----------
if not st.session_state.sources and not st.session_state.messages:
    st.subheader("Add something to study")
    st.write(
        "Upload a PDF or text file, or paste a link, from the sidebar. "
        "Once it's indexed you can ask questions and every answer will cite "
        "the page or timestamp it came from."
    )

# ---------- the conversation ----------
# Replay the whole history top to bottom. The script re-runs on every
# interaction, so this loop is what redraws the chat each time.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.caption(msg["intent"].upper())        # TUTOR / QUIZ / RESEARCH
        st.write(msg["content"])
        if msg.get("chunks"):
            with st.expander("Retrieved chunks"):
                for c in msg["chunks"]:
                    st.text(c)

# ---------- chat input ----------
# Returns None on most re-runs; returns the typed string on the run
# where the user pressed enter.
question = st.chat_input("Ask anything about your material...")

if question:
    # 1. record what the user said
    st.session_state.messages.append({"role": "user", "content": question})

    # 2. ask the API
    with st.spinner("Thinking..."):
        r = requests.post(
            f"{API_URL}/ask",
            json={"question": question, "user_id": USER_ID},
        )
    data = r.json()      # {"answer": str, "intent": str, "chunks": list[str]}

    # 3. record what the assistant said
    st.session_state.messages.append({
        "role": "assistant",
        "content": data["answer"],
        "intent": data.get("intent", "tutor"),
        "chunks": data.get("chunks", []),
    })

    # 4. re-run so the two new messages paint immediately
    st.rerun()