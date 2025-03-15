import os
import io
import httpx
from PIL import Image
import pytesseract
from typing import Optional

# Configure Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

async def extract_text_from_image_url(image_url: str) -> Optional[str]:
    """
    Extract text from an image using OCR.
    
    Args:
        image_url: URL of the image to process
        
    Returns:
        Extracted text or None if extraction failed
    """
    try:
        # Download the image
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code != 200:
                print(f"Failed to download image: {response.status_code}")
                return None
            
            # Load the image
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            # Clean up the text
            text = text.strip()
            
            return text if text else None
    
    except Exception as e:
        print(f"OCR processing error: {str(e)}")
        return None

async def process_postcard_image(image_url: str) -> dict:
    """
    Process a postcard image to extract text and metadata.
    
    Args:
        image_url: URL of the postcard image
        
    Returns:
        Dictionary containing extracted text and metadata
    """
    try:
        # Extract text using OCR
        extracted_text = await extract_text_from_image_url(image_url)
        
        if not extracted_text:
            return {"text": "", "date": None, "location": None}
        
        # Extract date from text
        from app.utils.aggregator import detect_date_in_text
        date = detect_date_in_text(extracted_text)
        
        # Extract location from text
        from app.utils.aggregator import detect_location_in_text
        location = detect_location_in_text(extracted_text)
        
        return {
            "text": extracted_text,
            "date": date,
            "location": location
        }
    
    except Exception as e:
        print(f"Postcard image processing error: {str(e)}")
        return {"text": "", "date": None, "location": None} 