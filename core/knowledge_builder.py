"""
知识库构建模块
负责从Markdown文件构建向量数据库
"""
import os
import shutil
from typing import Optional, List

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 尝试导入进度条
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    def tqdm(iterable, desc=""):
        """进度条降级实现"""
        return iterable


class KnowledgeBuilder:
    """知识库构建器"""
    
    def __init__(
        self,
        api_base: str,
        api_key: str,
        embed_model: str,
        db_path: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        batch_size: int = 32
    ):
        """
        初始化知识库构建器
        
        Args:
            api_base: API基础URL
            api_key: API密钥
            embed_model: 嵌入模型名称
            db_path: 向量数据库保存路径
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
            batch_size: 批处理大小
        """
        self.api_base = api_base
        self.api_key = api_key
        self.embed_model = embed_model
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size
        
        # 定义Markdown标题层级
        self.headers_to_split_on = [
            ("#", "Category"),
            ("##", "SubCategory"),
            ("###", "Topic"),
            ("####", "Item"),
        ]
    
    def load_markdown(self, file_path: str) -> str:
        """
        加载Markdown文件
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            文件内容字符串
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到文件: {file_path}")
        
        print(f"📖 正在读取文件: {file_path} ...")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def split_by_headers(self, markdown_text: str) -> List[Document]:
        """
        按Markdown标题结构化切分
        
        Args:
            markdown_text: Markdown文本内容
            
        Returns:
            切分后的文档列表
        """
        print("✂️  正在进行 Markdown 结构化切分...")
        
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )
        md_header_splits = markdown_splitter.split_text(markdown_text)
        
        print(f"   初步切分: 获得了 {len(md_header_splits)} 个语义块。")
        return md_header_splits
    
    def split_by_size(self, documents: List[Document]) -> List[Document]:
        """
        按字符大小二次切分（防止单个块过大）
        
        Args:
            documents: 文档列表
            
        Returns:
            二次切分后的文档列表
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        final_docs = text_splitter.split_documents(documents)
        print(f"   最终切分: 生成 {len(final_docs)} 个向量片段。")
        
        return final_docs
    
    def preview_chunks(self, documents: List[Document], num_samples: int = 3):
        """
        预览切分效果
        
        Args:
            documents: 文档列表
            num_samples: 预览样本数量
        """
        print(f"\n🧐 [切分效果抽查] 前 {num_samples} 个片段内容展示:")
        for i, doc in enumerate(documents[:num_samples]):
            print(f"--- Chunk {i+1} ---")
            print(f"Metadata: {doc.metadata}")
            content_preview = doc.page_content[:100]
            if len(doc.page_content) > 100:
                content_preview += "..."
            print(f"Content: {content_preview}")
            print("-" * 30)
    
    def clear_database(self):
        """清理旧数据库"""
        if os.path.exists(self.db_path):
            print(f"🗑️  清理旧数据库: {self.db_path}")
            shutil.rmtree(self.db_path)
    
    def create_embeddings(self) -> OpenAIEmbeddings:
        """
        创建嵌入模型实例
        
        Returns:
            OpenAIEmbeddings实例
        """
        print(f"\n🔌 初始化 Embedding: {self.embed_model} ...")
        return OpenAIEmbeddings(
            model=self.embed_model,
            openai_api_base=self.api_base,
            openai_api_key=self.api_key,
            chunk_size=32,
            check_embedding_ctx_length=False
        )
    
    def store_documents(
        self,
        documents: List[Document],
        embeddings: OpenAIEmbeddings
    ):
        """
        将文档存入向量数据库
        
        Args:
            documents: 文档列表
            embeddings: 嵌入模型实例
        """
        print("💾 存入 ChromaDB (分批处理)...")
        
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=self.db_path
        )
        
        # 分批写入
        total_batches = (len(documents) + self.batch_size - 1) // self.batch_size
        
        iterator = range(0, len(documents), self.batch_size)
        if TQDM_AVAILABLE:
            iterator = tqdm(iterator, desc="Writing Batches", total=total_batches)
        
        for i in iterator:
            batch = documents[i : i + self.batch_size]
            if batch:
                vectorstore.add_documents(batch)
    
    def build(
        self,
        markdown_path: str,
        clear_existing: bool = True,
        preview: bool = True
    ) -> dict:
        """
        完整的知识库构建流程
        
        Args:
            markdown_path: Markdown文件路径
            clear_existing: 是否清理已存在的数据库
            preview: 是否预览切分效果
            
        Returns:
            构建统计信息字典
        """
        # 1. 加载文件
        markdown_text = self.load_markdown(markdown_path)
        
        # 2. 结构化切分
        header_splits = self.split_by_headers(markdown_text)
        
        # 3. 二次切分
        final_docs = self.split_by_size(header_splits)
        
        # 4. 预览效果
        if preview:
            self.preview_chunks(final_docs)
        
        # 5. 清理旧库
        if clear_existing:
            self.clear_database()
        
        # 6. 创建嵌入
        embeddings = self.create_embeddings()
        
        # 7. 存储文档
        self.store_documents(final_docs, embeddings)
        
        print(f"\n✅ 知识库构建完成！")
        
        return {
            "total_chunks": len(final_docs),
            "header_splits": len(header_splits),
            "db_path": self.db_path,
            "embed_model": self.embed_model
        }


def build_knowledge_base(
    markdown_path: str,
    db_path: str,
    api_base: str,
    api_key: str,
    embed_model: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    batch_size: int = 32,
    clear_existing: bool = True,
    preview: bool = True
) -> dict:
    """
    工厂函数：构建知识库
    
    Args:
        markdown_path: Markdown文件路径
        db_path: 向量数据库保存路径
        api_base: API基础URL
        api_key: API密钥
        embed_model: 嵌入模型名称
        chunk_size: 文本块大小
        chunk_overlap: 文本块重叠大小
        batch_size: 批处理大小
        clear_existing: 是否清理已存在的数据库
        preview: 是否预览切分效果
        
    Returns:
        构建统计信息字典
    """
    builder = KnowledgeBuilder(
        api_base=api_base,
        api_key=api_key,
        embed_model=embed_model,
        db_path=db_path,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        batch_size=batch_size
    )
    
    return builder.build(
        markdown_path=markdown_path,
        clear_existing=clear_existing,
        preview=preview
    )
