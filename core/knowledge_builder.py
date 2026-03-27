"""
Knowledge base building module.
Builds a vector database from Markdown files.
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

# Try importing progress bar utility
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    def tqdm(iterable, desc=""):
        """Fallback progress bar implementation."""
        return iterable


class KnowledgeBuilder:
    """Knowledge base builder."""
    
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
        Initialize the knowledge base builder.
        
        Args:
            api_base: API base URL.
            api_key: API key.
            embed_model: Embedding model name.
            db_path: Vector database storage path.
            chunk_size: Text chunk size.
            chunk_overlap: Text chunk overlap size.
            batch_size: Batch size.
        """
        self.api_base = api_base
        self.api_key = api_key
        self.embed_model = embed_model
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size
        
        # Define Markdown header levels
        self.headers_to_split_on = [
            ("#", "Category"),
            ("##", "SubCategory"),
            ("###", "Topic"),
            ("####", "Item"),
        ]
    
    def load_markdown(self, file_path: str) -> str:
        """
        Load a Markdown file.
        
        Args:
            file_path: Markdown file path.
            
        Returns:
            File content string.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"📖 Reading file: {file_path} ...")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def split_by_headers(self, markdown_text: str) -> List[Document]:
        """
        Split text structurally by Markdown headers.
        
        Args:
            markdown_text: Markdown text content.
            
        Returns:
            List of split documents.
        """
        print("✂️  Performing structured Markdown splitting...")
        
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )
        md_header_splits = markdown_splitter.split_text(markdown_text)
        
        print(f"   Initial split: obtained {len(md_header_splits)} semantic chunks.")
        return md_header_splits
    
    def split_by_size(self, documents: List[Document]) -> List[Document]:
        """
        Perform secondary split by character size (to avoid oversized chunks).
        
        Args:
            documents: Document list.
            
        Returns:
            List of documents after secondary splitting.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        final_docs = text_splitter.split_documents(documents)
        print(f"   Final split: generated {len(final_docs)} vector chunks.")
        
        return final_docs
    
    def preview_chunks(self, documents: List[Document], num_samples: int = 3):
        """
        Preview splitting results.
        
        Args:
            documents: Document list.
            num_samples: Number of preview samples.
        """
        print(f"\n🧐 [Split Quality Spot Check] Showing first {num_samples} chunks:")
        for i, doc in enumerate(documents[:num_samples]):
            print(f"--- Chunk {i+1} ---")
            print(f"Metadata: {doc.metadata}")
            content_preview = doc.page_content[:100]
            if len(doc.page_content) > 100:
                content_preview += "..."
            print(f"Content: {content_preview}")
            print("-" * 30)
    
    def clear_database(self):
        """Clean up existing database."""
        if os.path.exists(self.db_path):
            print(f"🗑️  Cleaning existing database: {self.db_path}")
            shutil.rmtree(self.db_path)
    
    def create_embeddings(self) -> OpenAIEmbeddings:
        """
        Create an embedding model instance.
        
        Returns:
            OpenAIEmbeddings instance.
        """
        print(f"\n🔌 Initializing embedding model: {self.embed_model} ...")
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
        Store documents into the vector database.
        
        Args:
            documents: Document list.
            embeddings: Embedding model instance.
        """
        print("💾 Writing to ChromaDB (batch processing)...")
        
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=self.db_path
        )
        
        # Write in batches
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
        Full knowledge base build workflow.
        
        Args:
            markdown_path: Markdown file path.
            clear_existing: Whether to clear existing database.
            preview: Whether to preview splitting results.
            
        Returns:
            Build statistics dictionary.
        """
        # 1. Load file
        markdown_text = self.load_markdown(markdown_path)
        
        # 2. Structural split
        header_splits = self.split_by_headers(markdown_text)
        
        # 3. Secondary split
        final_docs = self.split_by_size(header_splits)
        
        # 4. Preview results
        if preview:
            self.preview_chunks(final_docs)
        
        # 5. Clean existing database
        if clear_existing:
            self.clear_database()
        
        # 6. Create embeddings
        embeddings = self.create_embeddings()
        
        # 7. Store documents
        self.store_documents(final_docs, embeddings)
        
        print(f"\n✅ Knowledge base build completed!")
        
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
    Factory function: build a knowledge base.
    
    Args:
        markdown_path: Markdown file path.
        db_path: Vector database storage path.
        api_base: API base URL.
        api_key: API key.
        embed_model: Embedding model name.
        chunk_size: Text chunk size.
        chunk_overlap: Text chunk overlap size.
        batch_size: Batch size.
        clear_existing: Whether to clear existing database.
        preview: Whether to preview splitting results.
        
    Returns:
        Build statistics dictionary.
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
