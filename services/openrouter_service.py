import aiohttp
import json
from typing import Dict, List, Any, Optional
from models.chatbot import ChatMessage

class OpenRouterService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    async def get_completion(
        self, 
        question: str,
        insect_context: Optional[Dict[str, Any]] = None,
        language: str = "es"  # Idioma por defecto: español
    ) -> Dict[str, Any]:
        """
        Get a completion from the OpenRouter API
        
        Args:
            messages: List of messages in the conversation
            model: Model to use for completion
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            insect_context: Optional context about the insect being discussed
        
        Returns:
            The API response as a dictionary
        """
        # Create a system message with insect information based on language
        if language.lower() == "es":
            system_content = (
                "Eres un entomólogo experto especializado en insectos. "
                "Proporciona información precisa, educativa y fascinante sobre insectos. "
                "Mantén un tono entusiasta y accesible. Responde SIEMPRE en español. "
                "IMPORTANTE: Sé muy conciso y breve. Limita tus respuestas a 1-2 párrafos cortos como máximo. "
                "Evita introducciones largas y ve directamente al punto principal. Usa frases cortas y directas."
            )
        else:  # English
            system_content = (
                "You are an expert entomologist specializing in insects. "
                "Provide accurate, educational, and fascinating information about insects. "
                "Maintain an enthusiastic and accessible tone. ALWAYS respond in English. "
                "IMPORTANT: Be very concise and brief. Limit your responses to 1-2 short paragraphs maximum. "
                "Avoid long introductions and go straight to the main point. Use short, direct sentences."
            )
        
        # If we have insect context, add it to the system message
        if insect_context and insect_context.get("name"):
            system_content += f"\n\nInformación sobre el insecto consultado ({insect_context['name']}):"
            
            if insect_context.get("scientific_name"):
                system_content += f"\n- Nombre científico: {insect_context['scientific_name']}"
            
            if insect_context.get("taxonomy"):
                system_content += f"\n- Taxonomía: {insect_context['taxonomy']}"
            
            if insect_context.get("description"):
                system_content += f"\n- Descripción: {insect_context['description']}"
        
        # Create messages array
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question}
        ]
        
        # Prepare the request payload with fixed parameters
        payload = {
            "model": "nousresearch/deephermes-3-mistral-24b-preview:free",
            "max_tokens": 150,  # Reducido a la mitad para respuestas más cortas
            "temperature": 0.7,
            "messages": messages
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
                
                return await response.json()
