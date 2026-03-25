#!/usr/bin/env python3
"""
Advanced Blender Code Generator for Complex 3D Assemblies
Specialized for handling complex components, assemblies, and industrial designs
"""

import os
import re
import json
from openai import OpenAI
from typing import List, Dict, Any


class AdvancedBlenderGenerator:
    def __init__(self, api_key: str, base_url: str = "https://api.gpt.ge/v1/", rag_db_path: str = "./rag"):
        """
        Initialize advanced Blender code generator for complex assemblies
        
        Args:
            api_key: OpenAI API key
            base_url: API base URL
            rag_db_path: RAG database path
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = "gpt-5-chat-latest"
        self.rag_db_path = rag_db_path
        
        # Load RAG library
        self.rag_templates = self._load_rag_library()
        self.rag_index = self._load_rag_index()
    
    def _load_rag_library(self) -> List[Dict[str, Any]]:
        """Load code templates from RAG library"""
        templates_file = os.path.join(self.rag_db_path, "code_templates.json")
        if os.path.exists(templates_file):
            with open(templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _load_rag_index(self) -> Dict[str, List[str]]:
        """Load index from RAG library"""
        index_file = os.path.join(self.rag_db_path, "templates_index.json")
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def search_rag(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Enhanced search for complex assembly components
        
        Args:
            query: Search query
            n_results: Return result count (increased for complex assemblies)
            
        Returns:
            List of related code snippets with relevance scores
        """
        # Enhanced keyword matching with multiple search strategies
        query_keywords = query.lower().split()
        
        # Calculate match score for each template with enhanced scoring
        scored_results = []
        for template in self.rag_templates:
            score = 0
            
            # Check description match (higher weight)
            desc_lower = template.get('description', '').lower()
            for keyword in query_keywords:
                if keyword in desc_lower:
                    score += 3  # Increased weight for description
                if keyword in template.get('code', '').lower():
                    score += 2  # Increased weight for code
            
            # Bonus for category relevance
            category = template.get('category', '').lower()
            if 'basic' in category and any(kw in ['cube', 'sphere', 'cylinder', 'create', 'build'] for kw in query_keywords):
                score += 2
            if 'lighting' in category and any(kw in ['light', 'illumination', 'shadow'] for kw in query_keywords):
                score += 2
            if 'camera' in category and any(kw in ['view', 'camera', 'perspective'] for kw in query_keywords):
                score += 2
            
            if score > 0:
                scored_results.append({
                    "template": template,
                    "score": score
                })
        
        # Sort by score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return first n_results results
        results = scored_results[:n_results]
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "code": result["template"]["code"],
                "description": result["template"]["description"],
                "category": result["template"]["category"],
                "similarity": result["score"]
            })
        
        return formatted_results
    
    def generate_with_web_search(self, prompt: str) -> str:
        """
        Generate code using Web search with enhanced queries
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated Blender code
        """
        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            input=prompt
        )
        
        # Extract response content
        if hasattr(response, 'output') and response.output:
            content = ""
            for item in response.output:
                if hasattr(item, 'content') and item.content:
                    for content_block in item.content:
                        if hasattr(content_block, 'text'):
                            content += content_block.text
        else:
            content = str(response)
        
        return content
    
    def generate_complex_assembly(self, text_input: str) -> str:
        """
        Generate code for complex 3D assemblies with advanced prompt
        
        Args:
            text_input: Input text description of complex assembly
            
        Returns:
            Generated Blender code
        """
        # Enhanced search for complex assemblies
        rag_results = self.search_rag(text_input, n_results=5)
        
        # Build comprehensive RAG context
        rag_context = ""
        if rag_results:
            rag_context += "\n" + "="*70 + "\n"
            rag_context += "AVAILABLE CODE TEMPLATES (Reference for Component Creation)\n"
            rag_context += "="*70 + "\n"
            for i, result in enumerate(rag_results):
                rag_context += f"\n--- Template {i+1}: {result['description']} ---\n"
                rag_context += f"Category: {result['category']} | Relevance Score: {result['similarity']}\n"
                rag_context += f"Code:\n{result['code']}\n"
                rag_context += "-"*70 + "\n"
        else:
            rag_context = "\nNo specific code templates found. Will generate custom solution.\n"
        
        # Advanced prompt for complex assemblies
        prompt = f"""You are a senior Blender API architect and 3D modeling expert. Your task is to create production-ready Python code for a complex 3D assembly.

PROJECT REQUIREMENT:
{text_input}

{rag_context}

COMPREHENSIVE CODE GENERATION FRAMEWORK:

1. SYSTEM ARCHITECTURE:
   - Design modular functions for each major component
   - Create a main assembly function that orchestrates component creation
   - Implement proper object naming conventions (e.g., 'Assembly_BasePlate_001')
   - Use Blender collections to organize components hierarchically
   - Create reusable utility functions for common operations

2. PRECISION MODELING:
   - Use exact dimensions and measurements from the requirements
   - Implement precise transformations with proper matrix operations
   - Use modifiers for non-destructive editing where possible
   - Handle boolean operations for complex geometry
   - Implement proper topology for downstream operations

3. ADVANCED ASSEMBLY TECHNIQUES:
   - Create parent-child relationships using proper constraints
   - Use drivers for parametric relationships between components
   - Implement instancing for repeated components
   - Handle complex joinery and connection points
   - Use shape keys or modifiers for variant configurations

4. MATERIAL & RENDERING SYSTEM:
   - Create procedural materials using Blender nodes
   - Implement proper UV unwrapping for textured components
   - Use texture coordinates and mapping for complex patterns
   - Set up material libraries for consistent appearance
   - Implement material overrides for different render passes

5. SCENE OPTIMIZATION:
   - Use collection instances for memory efficiency
   - Implement proper modifier stack optimization
   - Set up appropriate render layers and view layers
   - Configure lighting for optimal visibility and rendering
   - Implement proper scene cleanup and memory management

6. PROFESSIONAL CODE STANDARDS:
   - Add comprehensive docstrings for all functions
   - Include inline comments explaining complex operations
   - Implement proper error handling and validation
   - Add logging for debugging and monitoring
   - Use Python type hints where appropriate
   - Follow PEP 8 style guidelines

7. TECHNICAL IMPLEMENTATION:
   - Use web_search tool to get latest Blender API best practices
   - Implement proper scene cleanup: remove default objects
   - Use bpy.ops for high-level operations appropriately
   - Access data blocks directly for efficiency where possible
   - Handle different Blender versions gracefully
   - Ensure code is compatible with Blender 3.0+

8. DELIVERABLE REQUIREMENTS:
   - Single executable Python script
   - Complete import statements (bpy, mathutils, etc.)
   - No external dependencies beyond standard Blender
   - Include usage instructions in comments
   - Provide parameter customization at script start
   - Generate complete, renderable 3D assembly

9. QUALITY ASSURANCE:
   - Verify all objects are properly linked to scene
   - Ensure materials are correctly assigned
   - Check for proper parent relationships
   - Validate modifier stack integrity
   - Test render settings are appropriate

10. DOCUMENTATION:
    - Include assembly hierarchy description
    - Document key dimensions and measurements
    - Provide customization instructions
    - Explain component relationships
    - Include troubleshooting tips

SPECIFIC INSTRUCTIONS:
- Analyze the assembly requirements and break down into components
- Design appropriate hierarchy and organization
- Implement precise geometric operations
- Handle material assignments for each component
- Set up proper lighting and camera for preview
- Include render settings for final output
- Add error checking and user feedback
- Provide clear variable naming and structure

Please generate complete, production-ready Blender Python code that creates the requested complex 3D assembly. The code should be immediately executable and produce a professional-quality 3D model."""
        
        # Generate code with enhanced prompt
        generated_code = self.generate_with_web_search(prompt)
        
        # Extract code block
        code_block_pattern = r'```python\n(.*?)```'
        matches = re.findall(code_block_pattern, generated_code, re.DOTALL)
        
        if matches:
            return matches[0]
        else:
            return generated_code
    
    def save_code_to_file(self, code: str, file_path: str):
        """Save generated code to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"Complex assembly code has been saved to: {file_path}")
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG library statistics"""
        categories = {}
        for template in self.rag_templates:
            category = template.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_templates": len(self.rag_templates),
            "categories": categories,
            "db_path": self.rag_db_path
        }


def main():
    """Main function for complex assembly generation"""
    print("=== Advanced Blender Code Generator for Complex 3D Assemblies ===")
    print("Specialized for industrial design, mechanical assemblies, and complex components\n")
    
    # Initialize advanced generator
    generator = AdvancedBlenderGenerator(
        api_key="",
        base_url="https://api.gpt.ge/v1/",
        rag_db_path="./rag"
    )
    
    # Show RAG library statistics
    stats = generator.get_rag_stats()
    print(f"Available RAG templates: {stats['total_templates']}")
    print(f"Template categories: {stats['categories']}\n")
    
    # Get complex assembly description
    print("Enter your complex 3D assembly description.")
    print("Example: 'Create a mechanical gear assembly with 4 interlocking gears, mounting plate, and housing'")
    text_input = input("\nAssembly description: ")
    
    if not text_input.strip():
        print("Error: Assembly description cannot be empty.")
        return
    
    print(f"\n{'='*60}")
    print(f"Generating complex assembly: {text_input}")
    print(f"{'='*60}")
    print("This may take longer due to complexity analysis...\n")
    
    try:
        generated_code = generator.generate_complex_assembly(text_input)
        
        print(f"\n{'='*60}")
        print("GENERATED CODE")
        print(f"{'='*60}")
        print(generated_code)
        print(f"{'='*60}")
        
        # Save to file
        save_choice = input("\nDo you want to save this complex assembly code? (y/n): ")
        if save_choice.lower() == 'y':
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"complex_assembly_{timestamp}.py"
            file_path = input(f"Enter save path (default: {default_filename}): ") or default_filename
            generator.save_code_to_file(generated_code, file_path)
            print(f"\nComplex assembly code saved successfully!")
            print(f"File: {file_path}")
            print(f"\nTo use: Open Blender, go to Scripting workspace, and run the script.")
        
    except Exception as e:
        print(f"\nError generating complex assembly: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
