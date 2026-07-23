"""YouTube loader — turns a video URL into a Document from its transcript.
Different:extract the ID(user paste full URL), fetch captions, stitch them, handle no-transcript."""

from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document


def extract_video_id(url: str) -> str:
    """Pull the video ID out of a YouTube URL."""
    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    if "shorts/" in url:                                
        return url.split("shorts/")[1].split("?")[0]
    return url   # assume they already gave a bare ID


def load_youtube(url: str) -> list[Document]:
    video_id = extract_video_id(url)

    try:
        api = YouTubeTranscriptApi()                     # make an instance
        fetched = api.fetch(video_id)                    # .fetch() replaces get_transcript()
    except Exception as e:
        print(f"Could not get transcript for {url}: {e}")
        return []   # no transcript -> return empty list, don't crash

    # Stitch the snippets into one text block. Each snippet is {"text": ..., "start": ...}
    full_text = " ".join(snippet.text for snippet in fetched)

    doc = Document(
        page_content=full_text,
        metadata={"source": url, "type": "youtube"},
    )
    return [doc]   # same shape as every other loader: a list of Documents