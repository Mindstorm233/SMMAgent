"""
RAG检索模块
负责向量数据库的检索和上下文格式化
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
    创建向量数据库检索器
    
    Args:
        db_path: 向量数据库路径
        api_base: API基础URL
        api_key: API密钥
        embed_model: 嵌入模型名称
        k: 检索返回的文档数量
        
    Returns:
        检索器对象
    """
    embeddings = OpenAIEmbeddings(
        model=embed_model,
        openai_api_base=api_base,
        openai_api_key=api_key,
        check_embedding_ctx_length=False,
        chunk_size=32
    )
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"找不到数据库 {db_path}")
    
    vectorstore = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_context(retriever, query: str) -> tuple[str, int]:
    """
    检索相关上下文并格式化
    
    Args:
        retriever: 检索器对象
        query: 查询文本
        
    Returns:
        (格式化的上下文字符串, 检索到的文档数量)
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
    从文件加载并转义Prompt模板
    
    Args:
        file_path: Prompt文件路径
        
    Returns:
        转义后的模板字符串
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    # 通用转义逻辑
    escaped_text = raw_text.replace("{", "{{").replace("}", "}}")
    
    # 还原标准变量
    escaped_text = escaped_text.replace("{{context}}", "{context}")
    escaped_text = escaped_text.replace("{{question}}", "{question}")
    
    # 兼容旧变量名
    escaped_text = escaped_text.replace("{{ELEMENT_LIBRARY_JSON}}", "{context}")
    escaped_text = escaped_text.replace("{{PROTOCOL_TEXT}}", "{question}")
    
    return escaped_text
