import os
import base64
import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI
import re

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

# Initialize OpenAI client
if API_KEY:
    print(f"OpenAI Vision API key available: {bool(API_KEY)}")
    print(f"Using real OpenAI Vision API for text extraction")
else:
    print("ERROR: OpenAI Vision API key not found. Text extraction will fail!")

# In-memory cache to avoid reprocessing the same images
image_text_cache = {}

async def download_image(image_url: str) -> Optional[bytes]:
    """
    Download an image from a URL.
    
    Args:
        image_url: URL of the image
        
    Returns:
        Image data as bytes or None if download fails
    """
    try:
        # Skip download for mock or placeholder images
        if "placehold.co" in image_url or "example.com" in image_url or "dummyimage.com" in image_url:
            print(f"Skipping download for placeholder image: {image_url}")
            return None
            
        # Add a timeout to prevent hanging downloads
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, timeout=10.0)
            if response.status_code != 200:
                print(f"Failed to download image from {image_url}: {response.status_code}")
                return None
                
            return response.content
    except Exception as e:
        print(f"Error downloading image from {image_url}: {str(e)}")
        return None

async def extract_text_from_image(image_data: bytes) -> Optional[str]:
    """
    Extract text from an image using OpenAI's Vision model.
    Optimized for postcard text extraction.
    
    Args:
        image_data: Image as bytes
        
    Returns:
        Extracted text or None if extraction fails
    """
    if not API_KEY:
        print("ERROR: Cannot extract text - OpenAI API key is not set")
        return None
        
    max_retries = 3
    retry_delay = 1.0  # Initial delay in seconds
    
    for attempt in range(max_retries):
        try:
            print(f"DEBUG: Converting image to base64 (Attempt {attempt+1}/{max_retries})")
            # Convert image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            print(f"DEBUG: Sending request to OpenAI Vision API (Attempt {attempt+1}/{max_retries})")
            
            # First try with o1 model for better visual text recognition
            try:
                print("DEBUG: Trying o1 model")
                response = client.chat.completions.create(
                    model="o1",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a VERBATIM text extraction system for postcards. Your ONLY task is to extract the EXACT text visible in the image with 100% accuracy. NEVER invent, modify, or hallucinate text that is not visibly present in the image. If you're not certain about text, respond with NO_TEXT_FOUND. DO NOT refer to similar postcards or make educated guesses. Only report what you can clearly read."
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Read and transcribe ALL text visible in this postcard image EXACTLY as it appears, preserving formatting and line breaks. Don't add any information not clearly visible. If no text is visible or readable, respond with NO_TEXT_FOUND."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ]
                )
                print("DEBUG: Successfully used o1 model")
            except Exception as o1_error:
                print(f"DEBUG: Error using o1 model: {str(o1_error)}, falling back to gpt-4o")
                # Fall back to gpt-4o if o1 fails
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a VERBATIM text extraction system for postcards. Your ONLY task is to extract the EXACT text visible in the image with 100% accuracy. NEVER invent, modify, or hallucinate text that is not visibly present in the image. If you're not certain about text, respond with NO_TEXT_FOUND. DO NOT refer to similar postcards or make educated guesses. Only report what you can clearly read."
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Read and transcribe ALL text visible in this postcard image EXACTLY as it appears, preserving formatting and line breaks. Don't add any information not clearly visible. If no text is visible or readable, respond with NO_TEXT_FOUND."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ]
                )
            
            print(f"DEBUG: Received response from OpenAI Vision API (Attempt {attempt+1}/{max_retries})")
            
            # Validate the response
            if not response.choices or not response.choices[0].message or not response.choices[0].message.content:
                print(f"ERROR: Empty or invalid response from OpenAI API (Attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"DEBUG: Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                continue
                
            extracted_text = response.choices[0].message.content.strip()
            
            # Check for standardized "no text" response
            if extracted_text == "NO_TEXT_FOUND" or extracted_text.lower() == "no_text_found":
                print("DEBUG: OpenAI Vision API reported no text in the image")
                return None
            
            # Enhanced detection of various "no text" phrases
            no_text_patterns = [
                r'no text (found|detected|visible|present|identified)',
                r'(cannot|couldn\'t|could not|unable to) (detect|find|see|identify|read) (any )?text',
                r'(no|not) (any|a single)? (visible|readable|detectable|recognizable) text',
                r'the image (does not|doesn\'t) contain any (visible|readable) text',
                r'i (can\'t|cannot|am unable to) (read|see|detect|extract|find) (any )?text',
                r'(i\'m sorry|unfortunately)',
                r'i don\'t see any text',
                r'there is no (text|writing)',
                r'(image|postcard) (contains|has) no text',
                r'not able to extract',
                r'not clear enough'
            ]
            
            for pattern in no_text_patterns:
                if re.search(pattern, extracted_text.lower()):
                    print("DEBUG: OpenAI Vision API reported no text in the image (matched pattern)")
                    return None
            
            # Clean up the extracted text
            # Remove markdown code blocks if present
            cleaned_text = re.sub(r'```.*?```', '', extracted_text, flags=re.DOTALL)
            
            # Remove common prefixes that might be added
            cleaned_text = re.sub(r'^(Text:|The text reads:|Visible text:|Postcard text:|The postcard shows:)', '', cleaned_text).strip()
            
            # Remove any comments, explanations or notes
            cleaned_text = re.sub(r'\[.*?\]|\(.*?\)', '', cleaned_text)
            cleaned_text = re.sub(r'Note:.*?$', '', cleaned_text, flags=re.MULTILINE)
            
            # Replace excess newlines
            cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
            
            # Remove any commentary about text quality or explanations
            cleaned_text = re.sub(r'(\[|\(|\{\s*)(note|comment|text is|appears to be|might be|seems to be|text quality|partially visible).*?(\]|\)|\})\s*', '', 
                                 cleaned_text, flags=re.IGNORECASE)
            
            # Remove any statements about not being able to see text
            cleaned_text = re.sub(r'(I\'m sorry|Unfortunately).*?(visible|available|detected|found|present)\.?', '', 
                                 cleaned_text, flags=re.IGNORECASE)
            
            # Final cleanup of whitespace and unnecessary characters
            cleaned_text = cleaned_text.strip()
            if cleaned_text.startswith('"') and cleaned_text.endswith('"'):
                cleaned_text = cleaned_text[1:-1]
            
            # If after cleaning, the text is very short or empty, treat as no text
            if not cleaned_text or len(cleaned_text) < 3:
                print("DEBUG: After cleaning, text was too short or empty")
                return None
                
            print(f"DEBUG: Successfully extracted text ({len(cleaned_text)} chars): '{cleaned_text[:100]}...'")
            return cleaned_text
            
        except Exception as e:
            print(f"ERROR: Exception in text extraction (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                print(f"DEBUG: Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            
    print("ERROR: All extraction attempts failed")
    return None

async def analyze_image(image_url: str) -> Optional[str]:
    """
    Download an image and extract text from it.
    
    Args:
        image_url: URL of the image
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        # Skip empty or invalid URLs
        if not image_url or not isinstance(image_url, str):
            print(f"DEBUG: Skipping invalid image URL: {image_url}")
            return None
            
        # Check cache first
        if image_url in image_text_cache:
            print(f"DEBUG: Using cached text for image: {image_url}")
            return image_text_cache[image_url]
            
        print(f"DEBUG: Starting download for image: {image_url[:50]}...")
        # Download the image
        image_data = await download_image(image_url)
        if not image_data:
            print(f"DEBUG: Failed to download image: {image_url[:50]}...")
            return None
            
        print(f"DEBUG: Downloaded image ({len(image_data)/1024:.1f} KB), sending to OpenAI Vision API...")
        # Extract text from the image using the Vision API
        extracted_text = await extract_text_from_image(image_data)
        
        # Process the extracted text
        if extracted_text:
            # Clean up the text a bit (remove excessive newlines, etc.)
            cleaned_text = re.sub(r'\n{2,}', '\n', extracted_text).strip()
            
            # Save to cache for future use
            image_text_cache[image_url] = cleaned_text
            print(f"DEBUG: Successfully extracted text ({len(cleaned_text)} chars): '{cleaned_text[:100]}...'")
            return cleaned_text
        else:
            print(f"DEBUG: No text extracted from image: {image_url[:50]}...")
            return None
    except Exception as e:
        print(f"DEBUG: Error analyzing image {image_url[:50]}...: {str(e)}")
        return None 