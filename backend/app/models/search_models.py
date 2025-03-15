from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class SearchFilters(BaseModel):
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    location: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    sort_by: Optional[str] = "relevance"  # relevance, price_asc, price_desc, newest

class SearchRequest(BaseModel):
    query: str
    filters: Optional[SearchFilters] = None
    page: int = 1
    limit: int = 20

class SearchResult(BaseModel):
    source: str
    title: str
    image_url: str
    additional_images: Optional[List[str]] = None  # Additional images (e.g., back of postcard)
    price: float
    currency: str
    link: str
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    affiliate_link: Optional[str] = None
    image_text: Optional[str] = None  # Stores text extracted from the primary image
    additional_image_text: Optional[List[str]] = None  # Text from additional images

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    page: int
    limit: int
    enhanced_query: Optional[str] = None
    filters_applied: Optional[Dict[str, Any]] = None 