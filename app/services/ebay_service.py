import os
import httpx
import json
import base64
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from app.models.search_models import SearchResult, SearchFilters

# Load environment variables
load_dotenv()

# eBay API configuration
EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")
EBAY_DEV_ID = os.getenv("EBAY_DEV_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")
EBAY_AFFILIATE_ID = os.getenv("EBAY_AFFILIATE_ID", "")  # eBay Partner Network ID
EBAY_AUTH_TOKEN = os.getenv("EBAY_AUTH_TOKEN")  # Use the provided auth token

# eBay API endpoints
EBAY_OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

# Configuration options
USE_SANDBOX = False  # Set to False for production
USE_MOCK_DATA = False  # Disable mock data for real API usage

# For troubleshooting
print(f"DEBUG: eBay config - SANDBOX: {USE_SANDBOX}, MOCK_DATA: {USE_MOCK_DATA}")

# Update endpoints if using sandbox
if USE_SANDBOX:
    EBAY_OAUTH_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
    EBAY_SEARCH_URL = "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search"
    print("DEBUG: Using eBay Sandbox environment")

if USE_MOCK_DATA:
    print("DEBUG: Mock data enabled - will return placeholder results")

# eBay category ID for postcards
POSTCARD_CATEGORY_ID = "914"  # Postcards category ID

async def get_ebay_token() -> str:
    """
    Get OAuth token for eBay API access.
    
    Returns:
        OAuth access token as string
    """
    # If we're using mock data, just return a placeholder token
    if USE_SANDBOX and USE_MOCK_DATA:
        print("DEBUG: Using mock token since mock data is enabled")
        return "MockToken12345"
        
    # For development, always try to generate a new token instead of using stored token
    # This helps avoid 'insufficient permissions' errors with expired or invalid tokens
    if EBAY_APP_ID and EBAY_CLIENT_SECRET:
        print("DEBUG: Generating new eBay application token with credentials")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Encode credentials for Basic authentication
                credentials = f"{EBAY_APP_ID}:{EBAY_CLIENT_SECRET}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {encoded_credentials}"
                }
                
                # Request client_credentials grant for Application token (appropriate for Browse API)
                data = {
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope"
                }
                
                print(f"DEBUG: Requesting token from: {EBAY_OAUTH_URL}")
                print(f"DEBUG: Using app ID: {EBAY_APP_ID}")
                
                response = await client.post(EBAY_OAUTH_URL, headers=headers, data=data)
                
                if response.status_code != 200:
                    print(f"DEBUG: Failed to get eBay token: {response.status_code} - {response.text}")
                    # Fall back to stored token if generation fails
                    if EBAY_AUTH_TOKEN:
                        print("DEBUG: Falling back to stored token")
                        return EBAY_AUTH_TOKEN.strip()
                    raise Exception(f"Failed to get eBay token: {response.text}")
                
                token_data = response.json()
                token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", "unknown")
                print(f"DEBUG: Successfully generated new eBay token (expires in {expires_in} seconds): {token[:20]}...")
                return token
                
        except Exception as e:
            print(f"DEBUG: Exception during token generation: {str(e)}")
            # Fall back to stored token if available
            if EBAY_AUTH_TOKEN:
                print("DEBUG: Exception occurred, falling back to stored token")
                return EBAY_AUTH_TOKEN.strip()
            raise e
    
    # If we still have a stored token, use it as last resort    
    if EBAY_AUTH_TOKEN:
        print(f"DEBUG: Using pre-configured eBay auth token starting with: {EBAY_AUTH_TOKEN[:20]}...")
        print(f"DEBUG: Full token length: {len(EBAY_AUTH_TOKEN)}")
        
        # Handle case where token might have quotes from .env file
        cleaned_token = EBAY_AUTH_TOKEN
        if cleaned_token.startswith("'") and cleaned_token.endswith("'"):
            cleaned_token = cleaned_token[1:-1]
            print("DEBUG: Removed quotes from token")
        elif cleaned_token.startswith('"') and cleaned_token.endswith('"'):
            cleaned_token = cleaned_token[1:-1]
            print("DEBUG: Removed double quotes from token")
            
        # Ensure the token doesn't have any whitespace or line breaks
        cleaned_token = cleaned_token.strip()
        if cleaned_token != EBAY_AUTH_TOKEN.strip():
            print("DEBUG: Token had whitespace/newlines that were cleaned")
            
        print(f"DEBUG: Final cleaned token starts with: {cleaned_token[:20]}...")
        return cleaned_token
    
    # If we get here, we have no way to authenticate
    raise ValueError("eBay API credentials not configured properly")

async def search_ebay(query: str, filters: Optional[SearchFilters] = None, page: int = 1, limit: int = 20) -> List[SearchResult]:
    """
    Search for postcards on eBay.
    
    Args:
        query: The search query
        filters: Optional search filters
        page: Page number for pagination
        limit: Number of results per page
        
    Returns:
        List of SearchResult objects
    """
    try:
        if not EBAY_APP_ID and not EBAY_AUTH_TOKEN:
            print("eBay credentials not configured")
            return []
            
        # Get OAuth token
        try:
            token = await get_ebay_token()
            print(f"DEBUG: eBay token (first 20 chars): {token[:20] if token else 'None'}")
        except Exception as e:
            print(f"DEBUG: Failed to get eBay token: {str(e)}")
            return []
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Prepare query parameters
        params = {
            "q": query,
            "category_ids": POSTCARD_CATEGORY_ID,
            "limit": limit,
            "offset": offset,
            "sort": "newlyListed" if filters and filters.sort_by == "newest" else "bestMatch"
        }
        
        # Add price filters if provided
        if filters:
            if filters.price_min is not None or filters.price_max is not None:
                price_range = ""
                if filters.price_min is not None:
                    price_range += f"[{filters.price_min}.."
                else:
                    price_range += "["
                
                if filters.price_max is not None:
                    price_range += f"{filters.price_max}]"
                else:
                    price_range += "]"
                
                params["price"] = price_range
                
                # Add additional debug logging for price filter
                print(f"DEBUG: Using price filter: {price_range}")
        
        print(f"DEBUG: eBay search params: {params}")
        print(f"DEBUG: Using eBay search URL: {EBAY_SEARCH_URL}")
        
        # Make API request
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                "Content-Type": "application/json"
            }
            
            print(f"DEBUG: eBay request headers: {headers}")
            
            try:
                response = await client.get(EBAY_SEARCH_URL, headers=headers, params=params)
                
                if response.status_code != 200:
                    print(f"eBay search failed: {response.text}")
                    print(f"DEBUG: eBay response status: {response.status_code}")
                    print(f"DEBUG: eBay response headers: {response.headers}")
                    
                    # Only use mock data if explicitly enabled
                    if USE_MOCK_DATA:
                        print(f"DEBUG: Returning mock data in sandbox mode")
                        return get_mock_ebay_results(query, 3)
                    return []
                
                data = response.json()
                items = data.get("itemSummaries", [])
                
                print(f"DEBUG: eBay search returned {len(items)} items")
                if len(items) == 0 and "warnings" in data:
                    print(f"DEBUG: eBay API warnings: {data['warnings']}")
                
                # Convert to SearchResult objects
                results = []
                for item in items:
                    # Extract price
                    price = 0.0
                    currency = "USD"
                    if "price" in item:
                        price = float(item["price"]["value"])
                        currency = item["price"]["currency"]
                    
                    # Create affiliate link if affiliate ID is available
                    link = item.get("itemWebUrl", "")
                    affiliate_link = None
                    if EBAY_AFFILIATE_ID and link:
                        affiliate_link = f"{link}?mkrid={EBAY_AFFILIATE_ID}"
                    
                    # Extract date and location from title/subtitle if available
                    date = None
                    location = None
                    title = item.get("title", "")
                    subtitle = item.get("subtitle", "")
                    
                    # Simple extraction - in a real app, use more sophisticated NLP
                    # This is just a placeholder for the concept
                    import re
                    year_match = re.search(r'(18|19|20)\d{2}', title + " " + subtitle)
                    if year_match:
                        date = year_match.group(0)
                    
                    # Create SearchResult
                    result = SearchResult(
                        source="eBay",
                        title=title,
                        image_url=item.get("image", {}).get("imageUrl", ""),
                        additional_images=extract_additional_images(item),
                        price=price,
                        currency=currency,
                        link=link,
                        description=subtitle,
                        date=date,
                        location=location,
                        affiliate_link=affiliate_link
                    )
                    
                    results.append(result)
                
                return results
            except Exception as e:
                print(f"eBay API request error: {str(e)}")
                # Include traceback for more detailed debugging
                import traceback
                print(f"DEBUG: eBay API request traceback: {traceback.format_exc()}")
                
                # Only use mock data if explicitly enabled
                if USE_MOCK_DATA:
                    print(f"DEBUG: Returning mock data after exception in sandbox mode")
                    return get_mock_ebay_results(query, 3)
                return []
    
    except Exception as e:
        print(f"eBay search error: {str(e)}")
        if USE_MOCK_DATA:
            return get_mock_ebay_results(query, 3)
        return []

def get_mock_ebay_results(query: str, count: int = 5) -> List[SearchResult]:
    """
    Generate mock eBay search results for testing purposes.
    """
    print(f"DEBUG: Generating {count} mock eBay results for query: {query}")
    results = []
    for i in range(count):
        # Create mock data with the search query included
        price = float(5 + i * 3)
        
        # Adjust price based on any price filters in the query
        if "vintage" in query.lower():
            price = price * 2  # Vintage items cost more
            
        results.append(SearchResult(
            source="eBay (Mock)",
            title=f"Vintage {query} Postcard {1950 + i*10}s",
            image_url=f"https://placehold.co/150x150/png?text={query.replace(' ', '+')}+{i+1}",
            price=price,
            currency="USD",
            link=f"https://www.ebay.com/mock/item/{10000 + i}",
            description=f"Beautiful vintage postcard of {query} from the {1950 + i*10}s era",
            date=str(1950 + i*10),
            location=f"Location {i+1}",
            affiliate_link=None
        ))
    return results

def extract_additional_images(item: Dict[str, Any]) -> Optional[List[str]]:
    """
    Extract additional images from an eBay item.
    
    Args:
        item: eBay item data
        
    Returns:
        List of additional image URLs or None if no additional images
    """
    # Check if the item has additionalImages
    additional_images = item.get("additionalImages", [])
    if additional_images:
        return [img.get("imageUrl") for img in additional_images if img.get("imageUrl")]
        
    # For items with a galleryPlusPictureURL, use that as an additional image
    gallery_plus_url = item.get("galleryPlusPictureURL")
    if gallery_plus_url:
        return [gallery_plus_url]
        
    return None 