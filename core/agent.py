"""
Agent module.
Implements a two-stage compiler: Generator + Verifier.
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
    """Two-stage compiler for biochip design."""
    
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
        Initialize the compiler.
        
        Args:
            api_base: API base URL.
            api_key: API key.
            chat_model: Chat model name.
            embed_model: Embedding model name.
            db_path: Vector database path.
            compiler_prompt_path: Generator prompt path.
            verifier_prompt_path: Verifier prompt path.
            temperature: Model temperature parameter.
        """
        self.api_base = api_base
        self.api_key = api_key
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.db_path = db_path
        self.compiler_prompt_path = compiler_prompt_path
        self.verifier_prompt_path = verifier_prompt_path
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.chat_model,
            temperature=self.temperature,
            openai_api_base=self.api_base,
            openai_api_key=self.api_key
        )
        
        # Load prompt templates
        self.compiler_prompt = self._load_prompt(compiler_prompt_path)
        self.verifier_prompt = self._load_prompt(verifier_prompt_path)
    
    def _load_prompt(self, file_path: str) -> ChatPromptTemplate:
        """Load a prompt template."""
        template_str = load_prompt_template_from_file(file_path)
        return ChatPromptTemplate.from_template(template_str)
    
    def retrieve_knowledge(self, protocol_text: str) -> tuple[str, int]:
        """
        Retrieve relevant knowledge.
        
        Args:
            protocol_text: Protocol text.
            
        Returns:
            (Context string, document count)
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
        Generate an initial design (Generator stage).
        
        Args:
            protocol_text: Protocol text.
            context: Retrieved context.
            
        Returns:
            (Draft design, elapsed time)
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
        Verify and refine the design (Verifier stage).
        
        Args:
            draft_design: Draft design.
            context: Retrieved context.
            
        Returns:
            (Final design, elapsed time)
        """
        # Convert draft to JSON string
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
        Full compilation workflow.
        
        Args:
            protocol_text: Protocol text.
            
        Returns:
            Dictionary containing draft, final design, and statistics.
        """
        print(f"\n🚀 Starting two-stage compiler (Generator + Verifier)")
        print("=" * 60)
        
        # Stage 0: RAG retrieval
        print("\n🔍 Step 0: RAG retrieval (Sharing Context)...")
        context_str, doc_count = self.retrieve_knowledge(protocol_text)
        print(f"   ✅ Retrieved {doc_count} relevant rules.")
        
        # Stage 1: generation
        print("\n🏗️  Step 1: Initial design generation (Generator)...")
        draft_design, gen_time = self.generate_draft(protocol_text, context_str)
        print(f"   ✅ Draft generation completed (elapsed {gen_time:.2f}s)")
        print(f"   (Draft Reasoning: {draft_design.reasoning[:100]}...)")
        
        # Stage 2: verification
        print("\n🕵️  Step 2: Automatic verification and refinement (Verifier)...")
        final_design, ver_time = self.verify_and_refine(draft_design, context_str)
        print(f"   ✅ Verification and refinement completed (elapsed {ver_time:.2f}s)")
        
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
    Factory function: create a compiler instance.
    
    Args:
        api_base: API base URL.
        api_key: API key.
        chat_model: Chat model name.
        embed_model: Embedding model name.
        db_path: Vector database path.
        compiler_prompt_path: Generator prompt path.
        verifier_prompt_path: Verifier prompt path.
        temperature: Model temperature parameter.
        
    Returns:
        BioChipCompiler instance.
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
