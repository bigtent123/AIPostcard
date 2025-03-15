from typing import List, Dict, Any, Optional
from app.models.search_models import SearchResult, SearchFilters
import random
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

def aggregate_results(
    result_lists: List[List[SearchResult]], 
    filters: Optional[SearchFilters] = None,
    sort_by: str = "relevance"
) -> List[SearchResult]:
    """
    Aggregate search results from multiple sources.
    
    Args:
        result_lists: List of result lists from different sources
        filters: Optional filters to apply to the aggregated results
        sort_by: How to sort the results (relevance, price_asc, price_desc, newest)
        
    Returns:
        Combined and sorted list of search results
    """
    # Combine all results
    all_results = []
    for results in result_lists:
        all_results.extend(results)
    
    logger.debug(f"Total results before filtering: {len(all_results)}")
    logger.debug(f"Filters applied: {filters}")
    
    # Sort results
    if sort_by:
        if sort_by == "price_asc":
            all_results.sort(key=lambda x: x.price)
        elif sort_by == "price_desc":
            all_results.sort(key=lambda x: x.price, reverse=True)
        elif sort_by == "newest":
            # Sort by date if available (assuming newer dates are "greater")
            # If date is not available, use a secondary sort key
            def get_date_sort_key(result):
                if result.date and re.match(r'^\d{4}$', result.date):
                    return int(result.date)
                return 0  # Default for results without a year
                
            all_results.sort(key=get_date_sort_key, reverse=True)
        else:  # Default is "relevance" - already sorted by the individual APIs
            # In a real-world implementation, you might want to re-score for relevance here
            pass
    
    # Apply filters if provided
    if filters:
        filtered_result_lists = []
        
        # Process each source separately so we have results from all sources
        for results in result_lists:
            filtered_list = []
            
            for result in results:
                include_result = True
                
                # Apply year filters if provided
                if filters.year_min is not None and result.date:
                    # Extract year from date string
                    year_match = re.search(r'(18|19|20)\d{2}', result.date)
                    if year_match:
                        year = int(year_match.group(0))
                        if year < filters.year_min:
                            include_result = False
                            logger.debug(f"Filtering out result with year {year} < {filters.year_min}")
                            continue
                
                if filters.year_max is not None and result.date:
                    # Extract year from date string
                    year_match = re.search(r'(18|19|20)\d{2}', result.date)
                    if year_match:
                        year = int(year_match.group(0))
                        if year > filters.year_max:
                            include_result = False
                            logger.debug(f"Filtering out result with year {year} > {filters.year_max}")
                            continue
                
                # Apply location filter if provided
                if filters.location and result.location:
                    if filters.location.lower() not in result.location.lower():
                        include_result = False
                        logger.debug(f"Filtering out result with location {result.location} not matching {filters.location}")
                        continue
                
                # Apply price filters if provided
                if filters.price_min is not None:
                    if result.price < filters.price_min:
                        include_result = False
                        logger.debug(f"Filtering out result with price {result.price} < {filters.price_min}")
                        continue
                    
                if filters.price_max is not None:
                    if result.price > filters.price_max:
                        include_result = False
                        logger.debug(f"Filtering out result with price {result.price} > {filters.price_max}")
                        continue
                
                if include_result:
                    filtered_list.append(result)
            filtered_result_lists.append(filtered_list)
        
        # Interleave results from different sources
        interleaved_results = []
        max_results = max(len(results) for results in filtered_result_lists) if filtered_result_lists else 0
        
        for i in range(max_results):
            for results in filtered_result_lists:
                if i < len(results):
                    interleaved_results.append(results[i])
        
        # Remove duplicates (if any)
        seen_titles = set()
        unique_results = []
        
        for result in interleaved_results:
            # Use title and source as a simple deduplication key
            key = f"{result.title}|{result.source}"
            if key not in seen_titles:
                seen_titles.add(key)
                unique_results.append(result)
        
        return unique_results
    
    # If no filters applied, just return all results
    return all_results

def match_query_in_image_text(result: SearchResult, query_terms: List[str]) -> bool:
    """
    Check if any query terms appear in the image text.
    
    Args:
        result: The search result to check
        query_terms: List of search terms
        
    Returns:
        True if any query term appears in the image text
    """
    if not result.image_text:
        return False
    
    image_text_lower = result.image_text.lower()
    for term in query_terms:
        if term in image_text_lower:
            return True
    
    return False

def filter_results_by_image_text(results: List[SearchResult], query: str) -> List[SearchResult]:
    """
    Filter results to prioritize those with matching text in images.
    
    Args:
        results: List of search results
        query: Search query
        
    Returns:
        Filtered and reordered list of search results
    """
    # Break query into terms for matching
    query_terms = [term.lower() for term in query.split() if len(term) > 2]
    
    if not query_terms:
        return results
    
    # Separate results with matching image text
    matches = []
    non_matches = []
    
    for result in results:
        if match_query_in_image_text(result, query_terms):
            matches.append(result)
        else:
            non_matches.append(result)
    
    # Return matches first, followed by non-matches
    return matches + non_matches

def detect_date_in_text(text: str) -> Optional[str]:
    """
    Detect a year or date in text using simple regex.
    
    Args:
        text: Text to search for dates
        
    Returns:
        Detected year or None
    """
    import re
    
    # Look for years between 1800 and 2099
    year_match = re.search(r'\b(18|19|20)\d{2}\b', text)
    if year_match:
        return year_match.group(0)
    
    return None

def detect_location_in_text(text: str) -> Optional[str]:
    """
    Detect a location in text using simple keyword matching.
    
    Args:
        text: Text to search for locations
        
    Returns:
        Detected location or None
    """
    # This is a very simplified approach
    # In a real app, you would use a Named Entity Recognition (NER) model
    # or a more sophisticated location detection algorithm
    
    # List of common cities and countries
    common_locations = [
        "New York", "Paris", "London", "Tokyo", "Berlin", "Rome", "Madrid",
        "USA", "France", "UK", "Japan", "Germany", "Italy", "Spain",
        "Chicago", "San Francisco", "Los Angeles", "Boston", "Washington",
        "California", "Florida", "Texas", "New Jersey"
    ]
    
    for location in common_locations:
        if location.lower() in text.lower():
            return location
    
    return None 