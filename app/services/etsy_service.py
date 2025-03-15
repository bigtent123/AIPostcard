import os
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from app.models.search_models import SearchResult, SearchFilters

# Load environment variables
load_dotenv()

# Etsy API configuration
ETSY_API_KEY = os.getenv("ETSY_API_KEY")
ETSY_AFFILIATE_ID = os.getenv("ETSY_AFFILIATE_ID", "")  # Etsy affiliate ID

# Etsy API endpoints
ETSY_SEARCH_URL = "https://openapi.etsy.com/v3/application/listings/active"

# Etsy category for postcards
POSTCARD_CATEGORY = "paper_goods,postcards"

# Use mock data for development
USE_MOCK_DATA = False  # Set to False for production

async def search_etsy(query: str, filters: Optional[SearchFilters] = None, page: int = 1, limit: int = 20) -> List[SearchResult]:
    """
    Search for postcards on Etsy.
    
    Args:
        query: The search query
        filters: Optional search filters
        page: Page number for pagination
        limit: Number of results per page
        
    Returns:
        List of SearchResult objects
    """
    try:
        # Use mock data only if explicitly enabled
        if USE_MOCK_DATA:
            return get_mock_etsy_results(query, limit)
            
        if not ETSY_API_KEY:
            print("No Etsy API key found, falling back to empty results")
            return []
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Prepare query parameters
        params = {
            "api_key": ETSY_API_KEY,
            "keywords": query,
            "taxonomy_id": POSTCARD_CATEGORY,
            "limit": limit,
            "offset": offset,
            "includes": "Images,Shop"
        }
        
        # Add price filters if provided
        if filters:
            if filters.price_min is not None:
                params["min_price"] = filters.price_min
            if filters.price_max is not None:
                params["max_price"] = filters.price_max
            
            # Add sort order
            if filters.sort_by == "price_asc":
                params["sort_on"] = "price"
                params["sort_order"] = "asc"
            elif filters.sort_by == "price_desc":
                params["sort_on"] = "price"
                params["sort_order"] = "desc"
            elif filters.sort_by == "newest":
                params["sort_on"] = "created"
                params["sort_order"] = "desc"
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(ETSY_SEARCH_URL, params=params)
            
            if response.status_code != 200:
                print(f"Etsy search failed: {response.text}")
                return []
            
            data = response.json()
            listings = data.get("results", [])
            
            # Convert to SearchResult objects
            results = []
            for listing in listings:
                # Extract price
                price = float(listing.get("price", {}).get("amount", 0)) / 100  # Etsy prices are in cents
                currency = listing.get("price", {}).get("currency_code", "USD")
                
                # Get the first image URL
                image_url = ""
                if "images" in listing and listing["images"]:
                    image_url = listing["images"][0].get("url_570xN", "")
                
                # Create affiliate link if affiliate ID is available
                link = f"https://www.etsy.com/listing/{listing.get('listing_id')}"
                affiliate_link = None
                if ETSY_AFFILIATE_ID and link:
                    affiliate_link = f"{link}?utm_source=affiliate&utm_medium=api&utm_campaign={ETSY_AFFILIATE_ID}"
                
                # Extract date and location from title/description if available
                date = None
                location = None
                title = listing.get("title", "")
                description = listing.get("description", "")
                
                # Simple extraction - in a real app, use more sophisticated NLP
                import re
                year_match = re.search(r'(18|19|20)\d{2}', title + " " + description[:100])
                if year_match:
                    date = year_match.group(0)
                
                # Create SearchResult
                result = SearchResult(
                    source="Etsy",
                    title=title,
                    image_url=image_url,
                    price=price,
                    currency=currency,
                    link=link,
                    description=description[:200] + "..." if len(description) > 200 else description,
                    date=date,
                    location=location,
                    affiliate_link=affiliate_link
                )
                
                results.append(result)
            
            return results
    
    except Exception as e:
        print(f"Etsy search error: {str(e)}")
        return []

def get_mock_etsy_results(query: str, count: int = 5) -> List[SearchResult]:
    """
    Generate mock search results for Etsy.
    
    Args:
        query: The search query
        count: Number of mock results to generate
        
    Returns:
        List of mock SearchResult objects
    """
    results = []
    
    for i in range(count):
        # Generate a random price between $5 and $30
        price = 5.0 + (i * 3.5)
        
        result = SearchResult(
            source="Etsy",
            title=f"Vintage {query} Postcard {1920 + (i * 10)}",
            image_url=f"https://placehold.co/300x200/e65c00/white?text=Etsy+{query}+{i+1}",
            price=price,
            currency="USD",
            link=f"https://www.etsy.com/listing/mock{i}",
            description=f"Beautiful vintage postcard featuring {query}. From circa {1920 + (i * 10)}.",
            date=f"{1920 + (i * 10)}",
            location=["Paris", "New York", "London", "Tokyo", "Rome"][i % 5],
            affiliate_link=f"https://www.etsy.com/listing/mock{i}"
        )
        
        results.append(result)
    
    return results 