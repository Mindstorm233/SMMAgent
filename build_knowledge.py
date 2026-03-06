"""build_knowledge.py
Knowledge base construction script
Used to build a vector database from Markdown files
"""
import os
import argparse
from dotenv import load_dotenv
from core import build_knowledge_base

# Load environment variables
load_dotenv()


def main():
    """Main function"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Build RAG knowledge base")
    parser.add_argument(
        "--input",
        type=str,
        default="./data/knowledge.md",
        help="Path to the input Markdown file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./chroma_db",
        help="Path to the output vector database"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Text chunk size"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Text chunk overlap size"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size"
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Do not clear the existing database"
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Do not preview the chunk splitting result"
    )
    
    args = parser.parse_args()
    
    # Get configuration from environment variables
    API_BASE = os.getenv("API_BASE")
    API_KEY = os.getenv("API_KEY")
    EMBED_MODEL = os.getenv("embedding_model_name", "GLM-Embedding-2")
    
    # Validate required parameters
    if not API_BASE or not API_KEY:
        print("❌ Error: Please configure API_BASE and API_KEY in the .env file")
        return
    
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        return
    
    print("=" * 60)
    print("🏗️  Knowledge Base Builder")
    print("=" * 60)
    print(f"📄 Input file: {args.input}")
    print(f"💾 Output path: {args.output}")
    print(f"🤖 Embedding model: {EMBED_MODEL}")
    print(f"📏 Chunk size: {args.chunk_size} (overlap: {args.chunk_overlap})")
    print(f"📦 Batch size: {args.batch_size}")
    print("=" * 60)
    
    try:
        # Build the knowledge base
        stats = build_knowledge_base(
            markdown_path=args.input,
            db_path=args.output,
            api_base=API_BASE,
            api_key=API_KEY,
            embed_model=EMBED_MODEL,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            batch_size=args.batch_size,
            clear_existing=not args.no_clear,
            preview=not args.no_preview
        )
        
        # Print statistics
        print("\n" + "=" * 60)
        print("📊 Build Statistics")
        print("=" * 60)
        print(f"✅ Total document chunks: {stats['total_chunks']}")
        print(f"✅ Header splits: {stats['header_splits']}")
        print(f"✅ Database path: {stats['db_path']}")
        print(f"✅ Embedding model: {stats['embed_model']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
