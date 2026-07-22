"""RAG chain — the full question-to-answer flow.
Retrieve chunks, stuff them into a grounded prompt, LLM answers from them."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import llm
from rag.retrieve import retrieve


def format_chunks(chunks) -> str:
    """Turn the list of retrieved Documents into one text block for the prompt."""
    return "\n\n".join(chunk.page_content for chunk in chunks)


# The prompt: force the LLM to answer ONLY from the retrieved context.
prompt = ChatPromptTemplate.from_template(
    """You are a helpful study assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't know based on the provided documents."

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""
)


def ask(question: str) -> str:
    chunks = retrieve(question)                 # 1. get relevant chunks (milestone 5)
    context = format_chunks(chunks)             # 2. glue them into one text block
    messages = prompt.format_messages(          # 3. fill the prompt template
        context=context,
        question=question,
    )
    response = llm.invoke(messages)             # 4. LLM reads context + question, answers
    return response.content