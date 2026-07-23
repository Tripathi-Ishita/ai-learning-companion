from ingestion.pdf_loader import load_pdf
from ingestion.text_loader import load_notes
from ingestion.web_loader import load_web
from ingestion.youtube_loader import load_youtube


def load_source(source:str,source_type:str):
    if source_type=="pdf":
        return load_pdf(source)
    elif source_type=="web":
        return load_web(source)
    elif source_type=="youtube":
        return load_youtube(source)
    elif source_type=="notes":
        return load_notes(source)
    else:
        raise ValueError(f"Unsupported source_type: {source_type}")