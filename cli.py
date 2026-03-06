"""
命令行测试工具
用于测试生物芯片编译器和构建知识库
"""
import os
import json
import textwrap
import argparse
from dotenv import load_dotenv
from core import create_compiler, build_knowledge_base

# 加载环境变量
load_dotenv()


def print_section(title: str, char: str = "=", width: int = 60):
    """打印分隔线"""
    print(f"\n{char * width}")
    print(title)
    print(char * width)


def print_design_comparison(draft, final, stats):
    """打印设计对比报告"""
    print_section("📊 审查报告 (Review Report)", "-")
    
    print("\n1️⃣  [Generator] 初步设计思路:")
    print(textwrap.fill(draft.reasoning, width=80))
    print("\n" + "-" * 40 + "\n")
    
    print("2️⃣  [Verifier] 审查与修正意见:")
    print(textwrap.fill(final.reasoning, width=80))
    
    # 变更统计
    inst_diff = stats["final_instances"] - stats["draft_instances"]
    conn_diff = stats["final_connections"] - stats["draft_connections"]
    
    print(f"\n📈 变更统计:")
    print(f"   元件数量: {stats['draft_instances']} → {stats['final_instances']} "
          f"({'+'if inst_diff >= 0 else ''}{inst_diff})")
    print(f"   连接数量: {stats['draft_connections']} → {stats['final_connections']} "
          f"({'+'if conn_diff >= 0 else ''}{conn_diff})")
    print(f"\n⏱️  性能统计:")
    print(f"   生成耗时: {stats['gen_time']:.2f}s")
    print(f"   校验耗时: {stats['ver_time']:.2f}s")
    print(f"   总耗时: {stats['gen_time'] + stats['ver_time']:.2f}s")


def save_design(design, output_path: str):
    """保存设计到文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(design.model_dump(), f, indent=2, ensure_ascii=False)
    print(f"\n📁 最终设计已保存至: {output_path}")


def run_compiler(args):
    """运行编译器"""
    # 配置参数
    API_BASE = os.getenv("API_BASE")
    API_KEY = os.getenv("API_KEY")
    CHAT_MODEL = os.getenv("llm_model_name", "DeepSeek-V3.2")
    EMBED_MODEL = os.getenv("embedding_model_name", "GLM-Embedding-2")
    
    DB_PATH = args.db_path or "./chroma_db"
    COMPILER_PROMPT_PATH = args.compiler_prompt or "./data/compiler_prompt.md"
    VERIFIER_PROMPT_PATH = args.verifier_prompt or "./data/verifier_prompt.md"
    OUTPUT_PATH = args.output or "./data/final_design.json"
    
    # 测试协议（可以从文件读取或使用默认）
    if args.protocol:
        with open(args.protocol, "r", encoding="utf-8") as f:
            user_protocol = f.read()
    else:
        user_protocol = """
        操作步骤：
        1. 取400μL样本加入到1.5mL无核酸酶离心管中，再向离心管中依次加入10μL去宿主试剂SA， 50μL去宿主缓冲液，10μL去宿主试剂M，放置到恒温震荡金属浴上37℃、1000rpm反应5min；
        """
    
    try:
        # 创建编译器
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
        
        # 执行编译
        result = compiler.compile(user_protocol)
        
        # 打印对比报告
        print_design_comparison(
            result["draft"],
            result["final"],
            result["stats"]
        )
        
        # 保存结果
        save_design(result["final"], OUTPUT_PATH)
        
        print("=" * 60)
        print("✅ 编译完成！")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def run_build_kb(args):
    """构建知识库"""
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
        print("📊 构建统计")
        print("=" * 60)
        print(f"✅ 总文档块数: {stats['total_chunks']}")
        print(f"✅ 标题切分数: {stats['header_splits']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="生物芯片编译器CLI工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 编译器子命令
    compile_parser = subparsers.add_parser("compile", help="运行编译器")
    compile_parser.add_argument("--protocol", type=str, help="协议文件路径")
    compile_parser.add_argument("--db-path", type=str, help="向量数据库路径")
    compile_parser.add_argument("--compiler-prompt", type=str, help="编译器Prompt路径")
    compile_parser.add_argument("--verifier-prompt", type=str, help="校验器Prompt路径")
    compile_parser.add_argument("--output", type=str, help="输出文件路径")
    
    # 知识库构建子命令
    kb_parser = subparsers.add_parser("build-kb", help="构建知识库")
    kb_parser.add_argument("--input", type=str, default="./data/knowledge.md", help="输入Markdown文件")
    kb_parser.add_argument("--output", type=str, default="./chroma_db", help="输出数据库路径")
    kb_parser.add_argument("--chunk-size", type=int, default=500, help="文本块大小")
    kb_parser.add_argument("--chunk-overlap", type=int, default=50, help="文本块重叠")
    kb_parser.add_argument("--batch-size", type=int, default=32, help="批处理大小")
    kb_parser.add_argument("--no-clear", action="store_true", help="不清理旧数据库")
    kb_parser.add_argument("--no-preview", action="store_true", help="不预览切分效果")
    
    args = parser.parse_args()
    
    if args.command == "compile":
        run_compiler(args)
    elif args.command == "build-kb":
        run_build_kb(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
