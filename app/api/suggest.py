from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from app.services.gpt_service import generate_suggestions

router = APIRouter()

class SuggestionResponse(BaseModel):
    suggestions: List[str]
    original_query: str

@router.get("/suggest", response_model=SuggestionResponse)
async def get_suggestions(
    query: str = Query(..., description="Partial search query to get suggestions for"),
    limit: int = Query(5, description="Number of suggestions to return")
):
    try:
        if not query or len(query.strip()) < 2:
            return SuggestionResponse(
                suggestions=[],
                original_query=query
            )
        
        suggestions = await generate_suggestions(query, limit)
        
        return SuggestionResponse(
            suggestions=suggestions,
            original_query=query
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}") 