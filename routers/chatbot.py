from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from models.chatbot import ChatRequest, ChatCompletionResponse
from services.service_provider import get_openrouter_service, get_inaturalist_service

router = APIRouter(
    prefix="/api/chatbot",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
)

@router.post("/chat")
async def chat_with_entomologist(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat with the virtual entomologist about insects
    """
    openrouter_service = get_openrouter_service()
    
    # Prepare insect context if insect_id is provided
    insect_context = None
    if request.insect_id:
        try:
            inaturalist_service = get_inaturalist_service()
            insect_data = await inaturalist_service.get_species_info(request.insect_id, locale="es")
            
            if insect_data and insect_data.get("results"):
                insect = insect_data["results"][0]
                insect_context = {
                    "name": insect.get("preferred_common_name") or insect.get("name"),
                    "scientific_name": insect.get("name"),
                    "taxonomy": ", ".join([
                        f"{rank}: {name}" 
                        for rank, name in insect.get("ancestry_names", {}).items()
                    ]) if insect.get("ancestry_names") else None,
                    "description": insect.get("wikipedia_summary")
                }
        except Exception as e:
            # If we can't get insect info, continue without context
            pass
    elif request.insect_name:
        # If only name is provided, use that as minimal context
        insect_context = {"name": request.insect_name}
    
    try:
        # Get response from OpenRouter
        full_response = await openrouter_service.get_completion(
            question=request.question,
            insect_context=insect_context,
            language=request.language
        )
        
        # Simplify the response for the client
        if full_response and full_response.get("choices") and len(full_response["choices"]) > 0:
            answer = full_response["choices"][0]["message"]["content"]
            return {
                "answer": answer,
                "insect_info": insect_context
            }
        else:
            return {
                "answer": "Lo siento, no pude procesar tu pregunta en este momento.",
                "insect_info": insect_context
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
