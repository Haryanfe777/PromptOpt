import openai
import os
import time
from typing import List, Optional
from app.models.chat import ChatMessage, ChatRequest, ChatResponse
from app.models.prompt import Prompt

class LLMService:
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
        )
        
        # Default HR prompts
        self.default_prompts = {
            "recruiting": """You are an HR assistant specializing in recruiting. 
            Help with job postings, candidate screening, interview questions, and hiring processes. 
            Be professional, helpful, and provide actionable advice.""",
            
            "onboarding": """You are an HR assistant specializing in employee onboarding. 
            Help new employees with company policies, procedures, benefits, and getting started. 
            Be welcoming, informative, and thorough.""",
            
            "general": """You are a helpful HR assistant. 
            Answer questions about HR policies, procedures, benefits, and workplace issues. 
            Be professional, accurate, and supportive."""
        }
    
    def get_prompt_content(self, prompt_id: Optional[int] = None) -> str:
        """Get prompt content by ID or return default"""
        if prompt_id:
            # TODO: Fetch from database when implemented
            # For now, return default general prompt
            return self.default_prompts["general"]
        return self.default_prompts["general"]
    
    def format_conversation_history(self, history: List[ChatMessage]) -> List[dict]:
        """Format conversation history for OpenAI API"""
        messages = []
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        return messages
    
    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        """Generate response using OpenAI API"""
        start_time = time.time()
        
        try:
            # Get the prompt to use
            system_prompt = self.get_prompt_content(request.prompt_id)
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            if request.conversation_history:
                messages.extend(self.format_conversation_history(request.conversation_history))
            
            # Add current user message
            messages.append({
                "role": "user", 
                "content": request.message
            })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            # Extract response
            ai_response = response.choices[0].message.content or "I apologize, but I couldn't generate a response."
            response_time = time.time() - start_time
            
            return ChatResponse(
                response=ai_response,
                prompt_used=system_prompt,
                response_time=response_time,
                conversation_id=f"conv_{request.user_id}_{int(time.time())}"
            )
            
        except Exception as e:
            # Fallback response for errors
            return ChatResponse(
                response=f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}",
                prompt_used=system_prompt if 'system_prompt' in locals() else "fallback",
                response_time=time.time() - start_time
            )
