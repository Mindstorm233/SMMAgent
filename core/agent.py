"""
Agent模块
实现双阶段编译器：Generator + Verifier
"""
import json
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .schema import BioChipDesign
from .rag import (
    get_retriever,
    retrieve_context,
    load_prompt_template_from_file
)


class BioChipCompiler:
    """生物芯片双阶段编译器"""
    
    def __init__(
        self,
        api_base: str,
        api_key: str,
        chat_model: str,
        embed_model: str,
        db_path: str,
        compiler_prompt_path: str,
        verifier_prompt_path: str,
        temperature: float = 0.0
    ):
        """
        初始化编译器
        
        Args:
            api_base: API基础URL
            api_key: API密钥
            chat_model: 聊天模型名称
            embed_model: 嵌入模型名称
            db_path: 向量数据库路径
            compiler_prompt_path: 生成器Prompt路径
            verifier_prompt_path: 校验器Prompt路径
            temperature: 模型温度参数
        """
        self.api_base = api_base
        self.api_key = api_key
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.db_path = db_path
        self.compiler_prompt_path = compiler_prompt_path
        self.verifier_prompt_path = verifier_prompt_path
        self.temperature = temperature
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=self.chat_model,
            temperature=self.temperature,
            openai_api_base=self.api_base,
            openai_api_key=self.api_key
        )
        
        # 加载Prompt模板
        self.compiler_prompt = self._load_prompt(compiler_prompt_path)
        self.verifier_prompt = self._load_prompt(verifier_prompt_path)
    
    def _load_prompt(self, file_path: str) -> ChatPromptTemplate:
        """加载Prompt模板"""
        template_str = load_prompt_template_from_file(file_path)
        return ChatPromptTemplate.from_template(template_str)
    
    def retrieve_knowledge(self, protocol_text: str) -> tuple[str, int]:
        """
        检索相关知识
        
        Args:
            protocol_text: 协议文本
            
        Returns:
            (上下文字符串, 文档数量)
        """
        retriever = get_retriever(
            db_path=self.db_path,
            api_base=self.api_base,
            api_key=self.api_key,
            embed_model=self.embed_model,
            k=4
        )
        return retrieve_context(retriever, protocol_text)
    
    def generate_draft(
        self,
        protocol_text: str,
        context: str
    ) -> tuple[BioChipDesign, float]:
        """
        生成初步设计（Generator阶段）
        
        Args:
            protocol_text: 协议文本
            context: 检索到的上下文
            
        Returns:
            (草稿设计, 耗时)
        """
        prompt_val = self.compiler_prompt.invoke({
            "context": context,
            "question": protocol_text
        })
        
        generator = self.llm.with_structured_output(BioChipDesign)
        
        start_time = time.time()
        draft_design = generator.invoke(prompt_val)
        elapsed = time.time() - start_time
        
        return draft_design, elapsed
    
    def verify_and_refine(
        self,
        draft_design: BioChipDesign,
        context: str
    ) -> tuple[BioChipDesign, float]:
        """
        校验并修正设计（Verifier阶段）
        
        Args:
            draft_design: 草稿设计
            context: 检索到的上下文
            
        Returns:
            (最终设计, 耗时)
        """
        # 将草稿转为JSON字符串
        draft_json_str = json.dumps(
            draft_design.model_dump(),
            ensure_ascii=False
        )
        
        verifier_val = self.verifier_prompt.invoke({
            "context": context,
            "question": draft_json_str
        })
        
        verifier = self.llm.with_structured_output(BioChipDesign)
        
        start_time = time.time()
        final_design = verifier.invoke(verifier_val)
        elapsed = time.time() - start_time
        
        return final_design, elapsed
    
    def compile(self, protocol_text: str) -> dict:
        """
        完整编译流程
        
        Args:
            protocol_text: 协议文本
            
        Returns:
            包含草稿、最终设计和统计信息的字典
        """
        print(f"\n🚀 启动双阶段编译器 (Generator + Verifier)")
        print("=" * 60)
        
        # 阶段0: RAG检索
        print("\n🔍 Step 0: RAG 检索 (Sharing Context)...")
        context_str, doc_count = self.retrieve_knowledge(protocol_text)
        print(f"   ✅ 检索到 {doc_count} 条相关规则。")
        
        # 阶段1: 生成
        print("\n🏗️  Step 1: 初步设计生成 (Generator)...")
        draft_design, gen_time = self.generate_draft(protocol_text, context_str)
        print(f"   ✅ 草稿生成完毕 (耗时 {gen_time:.2f}s)")
        print(f"   (Draft Reasoning: {draft_design.reasoning[:100]}...)")
        
        # 阶段2: 校验
        print("\n🕵️  Step 2: 自动校验与修正 (Verifier)...")
        final_design, ver_time = self.verify_and_refine(draft_design, context_str)
        print(f"   ✅ 校验修正完毕 (耗时 {ver_time:.2f}s)")
        
        return {
            "draft": draft_design,
            "final": final_design,
            "stats": {
                "doc_count": doc_count,
                "gen_time": gen_time,
                "ver_time": ver_time,
                "draft_instances": len(draft_design.instances),
                "final_instances": len(final_design.instances),
                "draft_connections": len(draft_design.connections),
                "final_connections": len(final_design.connections)
            }
        }


def create_compiler(
    api_base: str,
    api_key: str,
    chat_model: str,
    embed_model: str,
    db_path: str,
    compiler_prompt_path: str,
    verifier_prompt_path: str,
    temperature: float = 0.0
) -> BioChipCompiler:
    """
    工厂函数：创建编译器实例
    
    Args:
        api_base: API基础URL
        api_key: API密钥
        chat_model: 聊天模型名称
        embed_model: 嵌入模型名称
        db_path: 向量数据库路径
        compiler_prompt_path: 生成器Prompt路径
        verifier_prompt_path: 校验器Prompt路径
        temperature: 模型温度参数
        
    Returns:
        BioChipCompiler实例
    """
    return BioChipCompiler(
        api_base=api_base,
        api_key=api_key,
        chat_model=chat_model,
        embed_model=embed_model,
        db_path=db_path,
        compiler_prompt_path=compiler_prompt_path,
        verifier_prompt_path=verifier_prompt_path,
        temperature=temperature
    )
