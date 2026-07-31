"""agents/profile.py

Per-user progress store. Separate from the checkpointer.

Checkpointer remembers the CONVERSATION (every message, keyed by thread_id).
This remembers the PERSON (topics seen / weak, keyed by user_id).
Different question, different lifetime -> different file.

Pure stdlib. Imports nothing from this project on purpose — that isolation
is the proof it's decoupled.
"""

import json
import os

PROFILE_PATH = "data/profiles.json"

# do not import this (private)
def _empty() -> dict:
    """A brand-new user's card."""
    return {"topics_seen": [], "topics_weak": []}


def load_profile(user_id: str) -> dict:
    """Return this user's card. Fresh empty card if file or user is missing.
    Read-only: never writes a default to disk."""
    if not os.path.exists(PROFILE_PATH):
        return _empty()
    with open(PROFILE_PATH) as f:
        store = json.load(f)
    return store.get(user_id, _empty())


def save_profile(user_id: str, profile: dict) -> None:
    """Write this user's card back, leaving other users untouched."""
    store = {}
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH) as f:
            store = json.load(f)
    store[user_id] = profile
    with open(PROFILE_PATH, "w") as f:
        json.dump(store, f, indent=2)

def mark_seen(user_id: str, topic: str) -> None:
    """Record that the user has encountered a topic (deduped)."""
    profile = load_profile(user_id)
    if topic not in profile["topics_seen"]:
        profile["topics_seen"].append(topic)
    save_profile(user_id, profile)


def mark_weak(user_id: str, topic: str) -> None:
    """Record that the user is struggling with a topic (deduped)."""
    profile = load_profile(user_id)
    if topic not in profile["topics_weak"]:
        profile["topics_weak"].append(topic)
    save_profile(user_id, profile)