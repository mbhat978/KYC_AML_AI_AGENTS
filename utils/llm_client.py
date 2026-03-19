"""
LLM Client wrapper for multi-provider support
"""
from typing import Optional, Dict, Any, List, Type
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config.settings import settings
from loguru import logger


class LLMClient:
    """Unified LLM client supporting multiple providers"""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or settings.default_llm_provider
        self.model = model
        self._client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == "openai":
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model=self.model or settings.openai_model,
                temperature=0.2
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model=self.model or settings.anthropic_model,
                temperature=0.2
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            system_prompt: The system instruction
            user_message: The user's input
            context: Additional context to include
            
        Returns:
            Generated response text
        """
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            if context:
                context_str = f"\nContext: {context}"
                messages.append(HumanMessage(content=context_str))
            
            response = self._client.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise
    
    def generate_structured(
        self,
        system_prompt: str,
        user_message: str,
        schema: Type[BaseModel],
        context: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        """
        Generate a structured response using LangChain's with_structured_output
        
        This prevents JSON hallucinations and markdown wrapping by mathematically
        forcing the LLM to return a clean object matching the Pydantic schema.
        
        Args:
            system_prompt: The system instruction
            user_message: The user's input
            schema: Pydantic model class defining the expected output structure
            context: Additional context to include
            
        Returns:
            Pydantic model instance with structured data
        """
        try:
            # Create a structured output chain
            structured_llm = self._client.with_structured_output(schema)
            
            # Build the full prompt
            full_prompt = f"{system_prompt}\n\n{user_message}"
            if context:
                full_prompt += f"\n\nContext: {context}"
            
            response = structured_llm.invoke(full_prompt)
            return response
        except Exception as e:
            logger.error(f"Structured LLM generation failed: {str(e)}")
            raise
    
    async def agenerate(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Async version of generate"""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            if context:
                context_str = f"\nContext: {context}"
                messages.append(HumanMessage(content=context_str))
            
            response = await self._client.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Async LLM generation failed: {str(e)}")
            raise


def get_llm_client(provider: Optional[str] = None) -> LLMClient:
    """Factory function to get LLM client"""
    return LLMClient(provider=provider)