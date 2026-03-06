"""cli.py
Command-line testing tool
Used to test the biochip compiler and build the knowledge base
"""
import os
import json
import textwrap
import argparse
from dotenv import load_dotenv
from core import create_compiler, build_knowledge_base

# Load environment variables
load_dotenv()


def print_section(title: str, char: str = "=", width: int = 60):
    """Print a separator section"""
    print(f"\n{char * width}")
    print(title)
    print(char * width)


def print_design_comparison(draft, final, stats):
    """Print the design comparison report"""
    print_section("📊 Review Report", "-")
    
    print("\n1️⃣  [Generator] Initial design reasoning:")
    print(textwrap.fill(draft.reasoning, width=80))
    print("\n" + "-" * 40 + "\n")
    
    print("2️⃣  [Verifier] Review and revision comments:")
    print(textwrap.fill(final.reasoning, width=80))
    
    # Change statistics
    inst_diff = stats["final_instances"] - stats["draft_instances"]
    conn_diff = stats["final_connections"] - stats["draft_connections"]
    
    print(f"\n📈 Change Statistics:")
    print(f"   Component count: {stats['draft_instances']} → {stats['final_instances']} "
          f"({'+'if inst_diff >= 0 else ''}{inst_diff})")
    print(f"   Connection count: {stats['draft_connections']} → {stats['final_connections']} "
          f"({'+'if conn_diff >= 0 else ''}{conn_diff})")
    print(f"\n⏱️  Performance Statistics:")
    print(f"   Generation time: {stats['gen_time']:.2f}s")
    print(f"   Verification time: {stats['ver_time']:.2f}s")
    print(f"   Total time: {stats['gen_time'] + stats['ver_time']:.2f}s")


def save_design(design, output_path: str):
    """Save the design to a file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(design.model_dump(), f, indent=2, ensure_ascii=False)
    print(f"\n📁 Final design has been saved to: {output_path}")


def run_compiler(args):
    """Run the compiler"""
    # Configuration parameters
    API_BASE = os.getenv("API_BASE")
    API_KEY = os.getenv("API_KEY")
    CHAT_MODEL = os.getenv("llm_model_name", "DeepSeek-V3.2")
    EMBED_MODEL = os.getenv("embedding_model_name", "GLM-Embedding-2")
    
    DB_PATH = args.db_path or "./chroma_db"
    COMPILER_PROMPT_PATH = args.compiler_prompt or "./data/compiler_prompt.md"
    VERIFIER_PROMPT_PATH = args.verifier_prompt or "./data/verifier_prompt.md"
    OUTPUT_PATH = args.output or "./data/final_design.json"
    
    # Test protocol (can be loaded from a file or use the default)
    if args.protocol:
        with open(args.protocol, "r", encoding="utf-8") as f:
            user_protocol = f.read()
    else:
        user_protocol = """
        Operation steps:
        1. Add 400 μL sample to a 1.5 mL nuclease-free centrifuge tube, then sequentially add 10 μL host depletion reagent SA, 50 μL host depletion buffer, and 10 μL host depletion reagent M into the tube, and place it on a thermostatic shaking metal bath for reaction at 37°C and 1000 rpm for 5 min;
        """
    
    try:
        # Create compiler
        compiler = create_compiler(
            api_base=API_BASE,
            api_key=API_KEY,
            chat_model=CHAT_MODEL,
            embed_model=EMBED_MODEL,
            db_path=DB_PATH,
            compiler_prompt_path=COMPILER_PROMPT_PATH,
            verifier_prompt_path=VERIFIER_PROMPT_PATH,
            temperature=0.0
        )
        
        # Execute compilation
        result = compiler.compile(user_protocol)
        
        # Print comparison report
        print_design_comparison(
            result["draft"],
            result["final"],
            result["stats"]
        )
        
        # Save result
        save_design(result["final"], OUTPUT_PATH)
        
        print("=" * 60)
        print("✅ Compilation completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def run_build_kb(args):
    """Build the knowledge base"""
    API_BASE = os.getenv("API_BASE")
    API_KEY = os.getenv("API_KEY")
    EMBED_MODEL = os.getenv("embedding_model_name", "GLM-Embedding-2")
    
    try:
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
        
        print("\n" + "=" * 60)
        print("📊 Build Statistics")
        print("=" * 60)
        print(f"✅ Total document chunks: {stats['total_chunks']}")
        print(f"✅ Header splits: {stats['header_splits']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Biochip Compiler CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")
    
    # Compiler subcommand
    compile_parser = subparsers.add_parser("compile", help="Run the compiler")
    compile_parser.add_argument("--protocol", type=str, help="Path to the protocol file")
    compile_parser.add_argument("--db-path", type=str, help="Path to the vector database")
    compile_parser.add_argument("--compiler-prompt", type=str, help="Path to the compiler prompt")
    compile_parser.add_argument("--verifier-prompt", type=str, help="Path to the verifier prompt")
    compile_parser.add_argument("--output", type=str, help="Path to the output file")
    
    # Knowledge base build subcommand
    kb_parser = subparsers.add_parser("build-kb", help="Build the knowledge base")
    kb_parser.add_argument("--input", type=str, default="./data/knowledge.md", help="Input Markdown file")
    kb_parser.add_argument("--output", type=str, default="./chroma_db", help="Output database path")
    kb_parser.add_argument("--chunk-size", type=int, default=500, help="Text chunk size")
    kb_parser.add_argument("--chunk-overlap", type=int, default=50, help="Text chunk overlap")
    kb_parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    kb_parser.add_argument("--no-clear", action="store_true", help="Do not clear the existing database")
    kb_parser.add_argument("--no-preview", action="store_true", help="Do not preview the chunk splitting result")
    
    args = parser.parse_args()
    
    if args.command == "compile":
        run_compiler(args)
    elif args.command == "build-kb":
        run_build_kb(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
