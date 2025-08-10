import logging
from typing import List, Dict, Any
from core.config import settings


class ResponseGenerator:
    """
    Generates final answers using LLM based on retrieved document chunks.
    """
    
    @staticmethod
    def generate_answer(
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        vector_store=None,
        classification=None
    ) -> str:
        """
        Generate a final answer based on the question and retrieved chunks.
        
        Args:
            question: User's question
            retrieved_chunks: List of retrieved document chunks
            vector_store: Vector store instance (not used for now)
            classification: Classification result (not used for now)
            
        Returns:
            Generated answer as string
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Prepare context from retrieved chunks
            context = ResponseGenerator._prepare_context(retrieved_chunks)
            
            # Create prompt for answer generation
            prompt = ResponseGenerator._create_answer_prompt(question, context)
            
            # Generate answer using LLM
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful financial document analyst. Answer questions based on the provided document context. Be accurate and concise."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            logging.error(f"Error generating answer: {str(e)}")
            return "I apologize, but I encountered an error while generating the answer. Please try again."
    
    @staticmethod
    def _prepare_context(chunks: List[Dict[str, Any]]) -> str:
        """Prepare context string from retrieved chunks"""
        if not chunks:
            return "No relevant documents found."
        
        context_parts = []
        for i, chunk in enumerate(chunks[:5]):  # Limit to top 5 chunks
            content = chunk.get('content', '')
            company = chunk.get('company', 'Unknown')
            year = chunk.get('year', 'Unknown')
            
            if content.strip():
                context_parts.append(f"Document {i+1} ({company}, {year}):\n{content}\n")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def _create_answer_prompt(question: str, context: str) -> str:
        """Create the prompt for answer generation"""
        return f"""
Based on the following document context, please answer the user's question.

Context:
{context}

Question: {question}

Please provide a clear, accurate answer based on the information in the documents. If the information is not available in the provided context, say so clearly.
""" 