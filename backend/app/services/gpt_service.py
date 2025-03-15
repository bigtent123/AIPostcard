import os
from openai import OpenAI
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API with client-based approach
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
print(f"OpenAI API key available: {bool(api_key)}")

async def enhance_query(query: str) -> str:
    """
    Enhance a search query using GPT-4 to improve search results.
    
    Args:
        query: The original search query from the user
        
    Returns:
        An enhanced query with expanded terms and better structure
    """
    # Skip enhancement for very short queries or if API key is missing
    if len(query.strip()) < 3 or not api_key:
        print(f"Skipping enhancement for short query: '{query}' or missing API key")
        return query
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                You are a search query enhancement assistant. Your task is to take a basic search query 
                and enhance it to improve search results for vintage postcards. 
                Add relevant terms but keep the query concise.
                """},
                {"role": "user", "content": f"Enhance this postcard search query: {query}"}
            ],
            max_tokens=100,
            temperature=0.3
        )
        enhanced_query = response.choices[0].message.content.strip()
        print(f"Enhanced query: '{query}' -> '{enhanced_query}'")
        return enhanced_query
    except Exception as e:
        print(f"Query enhancement failed: {str(e)}")
        return query

async def generate_suggestions(query: str, limit: int = 5) -> List[str]:
    """
    Generate search suggestions based on a partial query using GPT
    
    Args:
        query: The partial query from the user
        limit: Maximum number of suggestions to return
        
    Returns:
        A list of search suggestions
    """
    # Return basic suggestions if API key is not set
    if not api_key:
        # Return basic suggestions related to postcards
        print("No OpenAI API key - returning basic suggestions")
        basic_suggestions = [
            f"{query} vintage postcard",
            f"{query} antique postcard",
            f"{query} historical postcard",
            f"{query} postcard collection",
            f"{query} rare postcard"
        ]
        return basic_suggestions[:limit]
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                You are a search suggestion assistant for a vintage postcard website.
                Based on the user's partial query, suggest relevant complete search queries.
                Only provide the suggestions, one per line, with no numbering or additional text.
                Focus on locations, themes, and time periods related to postcards.
                """},
                {"role": "user", "content": f"Generate {limit} search suggestions for: {query}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        suggestion_text = response.choices[0].message.content.strip()
        suggestions = [s.strip() for s in suggestion_text.split('\n') if s.strip()]
        return suggestions[:limit]
    except Exception as e:
        print(f"Suggestion generation failed: {str(e)}")
        # Fallback to basic suggestions
        basic_suggestions = [
            f"{query} vintage",
            f"{query} historic",
            f"{query} antique",
            f"{query} collection",
            f"{query} rare"
        ]
        return basic_suggestions[:limit]

async def detect_language_and_translate(query: str) -> tuple[str, str]:
    """
    Detect the language of a query and translate it to English if necessary
    
    Args:
        query: The search query from the user
        
    Returns:
        A tuple of (translated_query, detected_language_code)
    """
    # If API key is missing, just return original and assume English
    if not api_key:
        return query, "en"
        
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                You are a language detection and translation assistant.
                Detect the language of the user's text and translate it to English if it's not already in English.
                Respond in the format: "language_code|translated_text"
                Example: "fr|Hello" for French text translated to "Hello"
                If the text is already in English, respond with "en|original_text"
                """},
                {"role": "user", "content": query}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        parts = result.split('|', 1)
        
        if len(parts) == 2:
            lang_code, translated = parts
            return translated, lang_code
        else:
            print(f"Unexpected translation format: {result}")
            return query, "en"
    except Exception as e:
        print(f"Translation failed: {str(e)}")
        return query, "en" 