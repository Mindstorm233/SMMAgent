"""
知识库构建脚本
用于从Markdown文件构建向量数据库
"""
import os
import argparse
from dotenv import load_dotenv
from core import build_knowledge_base

# 加载环境变量
load_dotenv()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="构建RAG知识库")
    parser.add_argument(
        "--input",
        type=str,
        default="./data/knowledge.md",
        help="输入的Markdown文件路径"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./chroma_db",
        help="输出的向量数据库路径"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="文本块大小"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="文本块重叠大小"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="批处理大小"
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="不清理已存在的数据库"
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="不预览切分效果"
    )
    
    args = parser.parse_args()
    
    # 从环境变量获取配置
    API_BASE = os.getenv("API_BASE")
    API_KEY = os.getenv("API_KEY")
    EMBED_MODEL = os.getenv("embedding_model_name", "GLM-Embedding-2")
    
    # 验证必要参数
    if not API_BASE or not API_KEY:
        print("❌ 错误: 请在.env文件中配置API_BASE和API_KEY")
        return
    
    if not os.path.exists(args.input):
        print(f"❌ 错误: 找不到输入文件 {args.input}")
        return
    
    print("=" * 60)
    print("🏗️  知识库构建工具")
    print("=" * 60)
    print(f"📄 输入文件: {args.input}")
    print(f"💾 输出路径: {args.output}")
    print(f"🤖 嵌入模型: {EMBED_MODEL}")
    print(f"📏 块大小: {args.chunk_size} (重叠: {args.chunk_overlap})")
    print(f"📦 批大小: {args.batch_size}")
    print("=" * 60)
    
    try:
        # 构建知识库
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
        
        # 打印统计信息
        print("\n" + "=" * 60)
        print("📊 构建统计")
        print("=" * 60)
        print(f"✅ 总文档块数: {stats['total_chunks']}")
        print(f"✅ 标题切分数: {stats['header_splits']}")
        print(f"✅ 数据库路径: {stats['db_path']}")
        print(f"✅ 嵌入模型: {stats['embed_model']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
