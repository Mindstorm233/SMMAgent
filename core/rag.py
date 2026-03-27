"""
RAG retrieval module.
Responsible for vector database retrieval and context formatting.
"""
import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def get_retriever(
    db_path: str,
    api_base: str,
    api_key: str,
    embed_model: str,
    k: int = 4
):
    """
    Create a vector database retriever.
    
    Args:
        db_path: Vector database path.
        api_base: API base URL.
        api_key: API key.
        embed_model: Embedding model name.
        k: Number of documents to return.
        
    Returns:
        Retriever object.
    """
    embeddings = OpenAIEmbeddings(
        model=embed_model,
        openai_api_base=api_base,
        openai_api_key=api_key,
        check_embedding_ctx_length=False,
        chunk_size=32
    )
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    vectorstore = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_context(retriever, query: str) -> tuple[str, int]:
    """
    Retrieve relevant context and format it.
    
    Args:
        retriever: Retriever object.
        query: Query text.
        
    Returns:
        (Formatted context string, number of retrieved documents)
    """
    docs = retriever.invoke(query)
    
    formatted_context = []
    for i, doc in enumerate(docs):
        cat = doc.metadata.get('Category', 'Info')
        formatted_context.append(
            f"--- Ref {i+1} ({cat}) ---\n{doc.page_content}"
        )
    
    context_str = "\n\n".join(formatted_context)
    return context_str, len(docs)


def load_prompt_template_from_file(file_path: str) -> str:
    """
    Load and escape a prompt template from file.
    
    Args:
        file_path: Prompt file path.
        
    Returns:
        Escaped template string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    # Generic escaping logic
    escaped_text = raw_text.replace("{", "{{").replace("}", "}}")
    
    # Restore standard variables
    escaped_text = escaped_text.replace("{{context}}", "{context}")
    escaped_text = escaped_text.replace("{{question}}", "{question}")
    
    # Compatibility with legacy variable names
    escaped_text = escaped_text.replace("{{ELEMENT_LIBRARY_JSON}}", "{context}")
    escaped_text = escaped_text.replace("{{PROTOCOL_TEXT}}", "{question}")
    
    return escaped_text
