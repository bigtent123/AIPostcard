from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
import asyncio
import os
import time

from app.models.search_models import SearchFilters, SearchRequest, SearchResult, SearchResponse
from app.services.gpt_service import enhance_query
from app.services.ebay_service import search_ebay
from app.services.etsy_service import search_etsy
from app.services.hippostcard_service import search_hippostcard
from app.services.image_analysis_service import analyze_image, download_image, extract_text_from_image
from app.utils.aggregator import aggregate_results, filter_results_by_image_text

router = APIRouter()

# Create a semaphore to limit concurrent API calls to OpenAI
# This helps prevent rate limiting errors
MAX_CONCURRENT_REQUESTS = 5  # Adjust based on OpenAI rate limits and your account tier
api_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# Maximum number of postcards to process for text extraction
# Set to a higher number than before but still reasonable
MAX_POSTCARDS_TO_PROCESS = 50  # Reduced from 100 to 50 for faster processing

# Maximum time (in seconds) to spend on image processing before timing out
IMAGE_PROCESSING_TIMEOUT = 60

# Track which image URLs have already been processed to avoid duplicates
processed_images = set()

@router.post("/search", response_model=SearchResponse)
async def search_postcards(request: SearchRequest, background_tasks: BackgroundTasks = None):
    """
    Search for postcards across multiple services.
    
    Args:
        request: Search request containing query and filters
        
    Returns:
        Combined search results from all services
    """
    try:
        print(f"DEBUG: Starting search for query: {request.query}")
        
        # Get raw results from each service
        try:
            ebay_results = await search_ebay(
                request.query, 
                request.filters, 
                request.page, 
                request.limit
            )
            print(f"DEBUG: Got {len(ebay_results)} results from eBay")
        except Exception as e:
            print(f"DEBUG: Error in eBay search: {str(e)}")
            ebay_results = []
        
        try:
            etsy_results = await search_etsy(
                request.query, 
                request.filters, 
                request.page, 
                request.limit
            )
            print(f"DEBUG: Got {len(etsy_results)} results from Etsy")
        except Exception as e:
            print(f"DEBUG: Error in Etsy search: {str(e)}")
            etsy_results = []
        
        try:
            hippostcard_results = await search_hippostcard(
                request.query, 
                request.filters, 
                request.page, 
                request.limit
            )
            print(f"DEBUG: Got {len(hippostcard_results)} results from HipPostcard")
        except Exception as e:
            print(f"DEBUG: Error in HipPostcard search: {str(e)}")
            hippostcard_results = []
        
        # Enhance query using GPT-4 (if available)
        try:
            enhanced_query = await enhance_query(request.query)
            print(f"DEBUG: Enhanced query: {enhanced_query}")
        except Exception as e:
            print(f"DEBUG: Error enhancing query: {str(e)}")
            enhanced_query = None
        
        # Combine and sort results
        all_results = ebay_results + etsy_results + hippostcard_results
        print(f"DEBUG: Total combined results: {len(all_results)}")
        
        # Initialize text extraction fields to undefined to show loading state
        for result in all_results:
            # Explicitly set to undefined by not setting a value
            # This ensures the frontend will show "Extracting text..." instead of "No text detected"
            if hasattr(result, 'image_text'):
                delattr(result, 'image_text')
            if hasattr(result, 'additional_image_text'):
                delattr(result, 'additional_image_text')
        
        # Apply filters and sorting via the aggregator
        aggregated_results = aggregate_results(
            [all_results], 
            request.filters,
            sort_by=request.filters.sort_by if request.filters else "relevance"
        )
        print(f"DEBUG: Number of aggregated results after filtering: {len(aggregated_results)}")
        
        # Process first batch of images immediately for better user experience
        if aggregated_results:
            print("DEBUG: Processing first batch of images immediately for better user experience")
            # Process the front and back of the first few postcards immediately
            immediate_processing_limit = min(10, len(aggregated_results))
            immediate_batch = aggregated_results[:immediate_processing_limit]
            print(f"DEBUG: Immediately processing {immediate_processing_limit} postcards")
            
            # Create tasks for immediate processing
            immediate_tasks = []
            
            for result in immediate_batch:
                # Process main image (front of postcard)
                if result.image_url:
                    immediate_tasks.append(analyze_main_image(result))
                    print(f"DEBUG: Added task for front image: {result.title[:30]}...")
                
                # Process first additional image if available (back of postcard)
                if result.additional_images and len(result.additional_images) > 0:
                    immediate_tasks.append(analyze_additional_image(result, result.additional_images[0], 0))
                    print(f"DEBUG: Added task for back image: {result.title[:30]}...")
            
            # Process immediate batch with a reasonable timeout
            if immediate_tasks:
                print(f"DEBUG: Running {len(immediate_tasks)} immediate image processing tasks")
                try:
                    await asyncio.gather(*immediate_tasks)
                    print("DEBUG: Completed immediate image processing successfully")
                except Exception as e:
                    print(f"DEBUG: Error during immediate image processing: {str(e)}")
        
        # Schedule remaining processing as a background task
        if background_tasks:
            background_tasks.add_task(process_image_text, aggregated_results.copy(), request.query)
            print("DEBUG: Added background task for processing remaining images")
        else:
            # Process the remaining images in the background
            asyncio.create_task(process_image_text(aggregated_results.copy(), request.query))
            print("DEBUG: Created background task for processing remaining images")
        
        # Prepare response
        response = SearchResponse(
            results=aggregated_results,
            total=len(all_results),
            page=request.page,
            limit=request.limit,
            enhanced_query=enhanced_query,
            filters_applied=request.filters.dict() if request.filters else None
        )
        
        print(f"DEBUG: Successfully prepared response with {len(response.results)} results")
        return response
    except Exception as e:
        print(f"ERROR: Exception in search_postcards: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@router.get("/search", response_model=SearchResponse)
async def search_postcards_get(
    query: str = Query(..., description="Search query for postcards"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    location: Optional[str] = Query(None, description="Location filter"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    sort_by: Optional[str] = Query("relevance", description="Sort order"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Results per page"),
    background_tasks: BackgroundTasks = None
):
    try:
        print(f"DEBUG: GET search request received for query: {query}")
        filters = SearchFilters(
            year_min=year_min,
            year_max=year_max,
            location=location,
            price_min=price_min,
            price_max=price_max,
            sort_by=sort_by
        )
        
        request = SearchRequest(
            query=query,
            filters=filters,
            page=page,
            limit=limit
        )
        
        return await search_postcards(request, background_tasks)
    except Exception as e:
        print(f"ERROR: Exception in GET search endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

async def process_image_text(results: List[SearchResult], query: str):
    """
    Process images in search results to extract text.
    Process up to MAX_POSTCARDS_TO_PROCESS postcards to prevent endless loading.
    This runs in the background after the initial results are returned.
    
    Args:
        results: List of search results
        query: Original search query
    """
    start_time = time.time()
    
    # Skip processing if no results
    if not results:
        return
    
    # Create tasks for processing images
    main_image_tasks = []
    additional_image_tasks = []
    
    # Apply a reasonable limit to prevent endless processing
    results_to_process = results[:MAX_POSTCARDS_TO_PROCESS]
    
    # Process each result up to the limit
    for result in results_to_process:
        # Process the main image if it hasn't been processed yet and isn't already being processed
        if result.image_url and result.image_url not in processed_images:
            processed_images.add(result.image_url)
            main_image_tasks.append(analyze_main_image(result))
            
        # Process additional images if available
        if result.additional_images:
            for i, img_url in enumerate(result.additional_images):
                # Skip if this additional image is being processed
                if img_url in processed_images:
                    continue
                    
                processed_images.add(img_url)
                additional_image_tasks.append(analyze_additional_image(result, img_url, i))
    
    num_main_images = len(main_image_tasks)
    num_additional_images = len(additional_image_tasks)
    total_images = num_main_images + num_additional_images
    
    if total_images == 0:
        print("No new images to process")
        return
        
    print(f"Processing text for {total_images} total images ({num_main_images} main, {num_additional_images} additional) from {len(results_to_process)}/{len(results)} postcards")
    
    # First process main images (front of postcards)
    if main_image_tasks:
        print(f"Processing {num_main_images} main images (postcard fronts)")
        # Process in batches to avoid overwhelming the API
        batch_size = MAX_CONCURRENT_REQUESTS
        for i in range(0, len(main_image_tasks), batch_size):
            # Check if we've exceeded the timeout
            if time.time() - start_time > IMAGE_PROCESSING_TIMEOUT:
                print(f"Main image processing timed out after {IMAGE_PROCESSING_TIMEOUT} seconds. Processed {i} of {num_main_images} main images.")
                return
                
            batch = main_image_tasks[i:i+batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(main_image_tasks) + batch_size - 1)//batch_size
            
            print(f"Processing main image batch {batch_num}/{total_batches}: {len(batch)} images")
            
            try:
                await asyncio.wait_for(
                    asyncio.gather(*batch), 
                    timeout=30
                )
            except asyncio.TimeoutError:
                print(f"Main image batch {batch_num} timed out. Moving to next batch.")
                
            # Small delay between batches to avoid rate limits
            if i + batch_size < len(main_image_tasks):
                await asyncio.sleep(0.5)
    
    # Then process additional images (back of postcards)
    if additional_image_tasks:
        print(f"Processing {num_additional_images} additional images (postcard backs)")
        # Process in batches to avoid overwhelming the API
        batch_size = MAX_CONCURRENT_REQUESTS
        for i in range(0, len(additional_image_tasks), batch_size):
            # Check if we've exceeded the timeout
            if time.time() - start_time > IMAGE_PROCESSING_TIMEOUT:
                print(f"Additional image processing timed out after {IMAGE_PROCESSING_TIMEOUT} seconds. Processed {i} of {num_additional_images} additional images.")
                return
                
            batch = additional_image_tasks[i:i+batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(additional_image_tasks) + batch_size - 1)//batch_size
            
            print(f"Processing additional image batch {batch_num}/{total_batches}: {len(batch)} images")
            
            try:
                await asyncio.wait_for(
                    asyncio.gather(*batch), 
                    timeout=30
                )
            except asyncio.TimeoutError:
                print(f"Additional image batch {batch_num} timed out. Moving to next batch.")
                
            # Small delay between batches to avoid rate limits
            if i + batch_size < len(additional_image_tasks):
                await asyncio.sleep(0.5)
    
    print(f"Completed image text processing in {time.time() - start_time:.2f} seconds")

async def analyze_main_image(result: SearchResult):
    """
    Process the main image (front) of a search result to extract text.
    
    Args:
        result: Search result with the main image to analyze
    """
    try:
        print(f"DEBUG: Starting text extraction for main image: {result.title[:30]}...")
        
        # Skip if no image URL is available
        if not result.image_url:
            print(f"DEBUG: No main image URL for: {result.title[:30]}")
            result.image_text = ""  # Use empty string to indicate no text
            return
            
        # Check if this image has already been processed - use the cache in analyze_image
        async with api_semaphore:
            print(f"DEBUG: Extracting text from main image: {result.title[:30]}...")
            image_text = await analyze_image(result.image_url)
            
        # Update the result with extracted text - always use empty string for None to avoid undefined
        result.image_text = image_text if image_text is not None else ""
        
        if image_text:
            print(f"DEBUG: Successfully extracted text from main image of {result.title[:30]}: {image_text[:50]}...")
        else:
            print(f"DEBUG: No text extracted from main image of {result.title[:30]}")
    except Exception as e:
        print(f"ERROR: Failed to analyze main image for {result.title[:30]}: {str(e)}")
        # Set to empty string to indicate extraction failed
        result.image_text = ""

async def analyze_additional_image(result: SearchResult, image_url: str, index: int):
    """
    Process an additional image (e.g., back of postcard) to extract text.
    
    Args:
        result: Search result to update
        image_url: URL of the additional image
        index: Index of the additional image
    """
    try:
        print(f"DEBUG: Starting text extraction for additional image {index+1}: {result.title[:30]}...")
        
        # Skip if no image URL is available
        if not image_url:
            print(f"DEBUG: No URL for additional image {index+1} of: {result.title[:30]}")
            # Initialize the additional_image_text attribute if it doesn't exist
            if not hasattr(result, 'additional_image_text'):
                result.additional_image_text = []
            # Extend the list if needed
            while len(result.additional_image_text) <= index:
                result.additional_image_text.append("")
            return
        
        # Initialize additional_image_text if it doesn't exist
        if not hasattr(result, 'additional_image_text'):
            result.additional_image_text = []
        
        # Extend the list if needed to fit this index
        while len(result.additional_image_text) <= index:
            result.additional_image_text.append(None)
            
        # Extract text from the image
        async with api_semaphore:
            print(f"DEBUG: Extracting text from additional image {index+1}: {result.title[:30]}...")
            image_text = await analyze_image(image_url)
            
        # Update with extracted text (use empty string if None to avoid undefined)
        result.additional_image_text[index] = image_text if image_text is not None else ""
        
        if image_text:
            print(f"DEBUG: Successfully extracted text from additional image {index+1} of {result.title[:30]}: {image_text[:50]}...")
        else:
            print(f"DEBUG: No text extracted from additional image {index+1} of {result.title[:30]}")
    except Exception as e:
        print(f"ERROR: Failed to analyze additional image {index+1} for {result.title[:30]}: {str(e)}")
        # Ensure the additional_image_text is initialized
        if not hasattr(result, 'additional_image_text'):
            result.additional_image_text = []
        # Extend the list if needed and set empty string for error case
        while len(result.additional_image_text) <= index:
            result.additional_image_text.append("")
        # Update with empty string to indicate error
        result.additional_image_text[index] = ""

@router.get("/test-extraction", response_model=dict)
async def test_extraction():
    """Test endpoint to extract text from a predefined image."""
    try:
        # Test main image
        test_image = "https://i.ebayimg.com/images/g/YdEAAOSwlSxlsrq4/s-l1600.jpg"
        print(f"Testing text extraction from: {test_image}")
        
        # Extract text manually
        image_data = await download_image(test_image)
        if not image_data:
            return {"error": "Failed to download test image"}
            
        text = await extract_text_from_image(image_data)
        
        # Return both the raw extracted text and a cleaned version
        return {
            "status": "success",
            "image_url": test_image,
            "extracted_text": text or "No text extracted",
            "text_length": len(text) if text else 0,
        }
    except Exception as e:
        print(f"Error in test extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@router.post("/test-custom-extraction")
async def test_custom_extraction(request: dict):
    """Test endpoint to extract text from a user-provided image URL."""
    try:
        image_url = request.get("image_url")
        if not image_url:
            return {"error": "No image URL provided"}
            
        print(f"Testing custom text extraction from: {image_url}")
        
        # Extract text manually
        image_data = await download_image(image_url)
        if not image_data:
            return {"error": "Failed to download provided image"}
            
        text = await extract_text_from_image(image_data)
        
        # Return both the raw extracted text and a cleaned version
        return {
            "status": "success",
            "image_url": image_url,
            "extracted_text": text or "No text extracted",
            "text_length": len(text) if text else 0,
        }
    except Exception as e:
        print(f"Error in custom test extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)} 