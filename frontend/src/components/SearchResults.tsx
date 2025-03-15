'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';

interface SearchResult {
  source: string;
  title: string;
  image_url: string;
  additional_images?: string[];
  price: number;
  currency: string;
  link: string;
  description?: string;
  date?: string;
  location?: string;
  affiliate_link?: string;
  image_text?: string;
  additional_image_text?: string[];
}

interface SearchResultsProps {
  query: string;
  page: number;
  yearMin?: number;
  yearMax?: number;
  location?: string;
  priceMin?: number;
  priceMax?: number;
  sortBy?: string;
}

export function SearchResults({
  query,
  page = 1,
  yearMin,
  yearMax,
  location,
  priceMin,
  priceMax,
  sortBy = 'relevance'
}: SearchResultsProps) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enhancedQuery, setEnhancedQuery] = useState<string | null>(null);
  const [extractionTimeout, setExtractionTimeout] = useState(false);

  // Add timeout for extraction
  useEffect(() => {
    const timer = setTimeout(() => {
      setExtractionTimeout(true);
    }, 10000);  // 10 seconds

    return () => clearTimeout(timer);
  }, []);

  // Function to standardize text display 
  const standardizeTextDisplay = (text: string | null | undefined): string => {
    // 1. Still extracting
    if (text === undefined) return "extracting";
    
    // 2. No text found
    if (text === null || text === "") return "none";
    
    // 3. Check for various phrases indicating no text was found
    const noTextPhrases = [
      "unable to extract", 
      "can't extract",
      "sorry",
      "couldn't",
      "no text",
      "not visible",
      "not detected",
      "no text found",
      "no_text_found",
      "i don't see any",
      "cannot see"
    ];
    
    const textLower = text.toLowerCase();
    for (const phrase of noTextPhrases) {
      if (textLower.includes(phrase)) {
        return "none";
      }
    }
    
    // 4. If the text is extremely short, it might be incomplete extraction
    if (text.length < 5) return "none";
    
    // 5. Return actual text
    return text;
  };
  
  // Display text with consistent messaging
  const renderExtractedText = (textStatus: string) => {
    // Extracting text, but not timed out yet
    if (textStatus === "extracting" && !extractionTimeout) {
      return (
        <span className="text-blue-500">
          <span className="animate-pulse">Extracting text...</span>
        </span>
      );
    } 
    // No text detected or extraction timed out
    else if (textStatus === "none" || (textStatus === "extracting" && extractionTimeout)) {
      return <span className="text-gray-500">No text detected</span>;
    } 
    // Text was successfully extracted
    else {
      return (
        <div className="text-sm text-gray-700 break-words whitespace-pre-line">
          {textStatus}
        </div>
      );
    }
  };

  useEffect(() => {
    const fetchResults = async () => {
      if (!query) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // Build query parameters
        const params = new URLSearchParams();
        params.append('query', query);
        params.append('page', page.toString());
        
        if (yearMin !== undefined) params.append('year_min', yearMin.toString());
        if (yearMax !== undefined) params.append('year_max', yearMax.toString());
        if (location) params.append('location', location);
        if (priceMin !== undefined) params.append('price_min', priceMin.toString());
        if (priceMax !== undefined) params.append('price_max', priceMax.toString());
        if (sortBy) params.append('sort_by', sortBy);
        
        // Make API request with proper error handling
        const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'}/api/search?${params.toString()}`;
        
        console.log(`Fetching search results from: ${apiUrl}`);
        
        const response = await fetch(apiUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          mode: 'cors',
        });
        
        if (!response.ok) {
          throw new Error(`Search failed: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log("Search response data:", data);
        setResults(data.results || []);
        setTotal(data.total || 0);
        setEnhancedQuery(data.enhanced_query || null);
      } catch (err) {
        console.error('Error fetching search results:', err);
        setError('Failed to fetch search results. Please try again later.');
        setResults([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    };
    
    fetchResults();
  }, [query, page, yearMin, yearMax, location, priceMin, priceMax, sortBy]);

  if (loading) {
    return <div className="text-center py-12">Loading results...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 dark:text-red-400 mb-4">{error}</div>
        <button 
          onClick={() => window.location.reload()}
          className="btn-primary"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Results header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">
          {total} {total === 1 ? 'result' : 'results'} for "{query}"
        </h1>
        
        {enhancedQuery && enhancedQuery !== query && (
          <p className="text-gray-600 dark:text-gray-400">
            Search enhanced to: "{enhancedQuery}"
          </p>
        )}
      </div>
      
      {/* Results grid */}
      {results.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((result, index) => (
            <div key={index} className="card">
              <div className="relative h-48 overflow-hidden">
                <Image
                  src={result.image_url}
                  alt={result.title}
                  fill
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                  className="object-cover"
                  onError={(e) => {
                    // Fallback image if the original fails to load
                    (e.target as HTMLImageElement).src = 'https://placehold.co/300x200/gray/white?text=No+Image';
                  }}
                />
                <div className="absolute top-2 left-2 bg-white dark:bg-slate-800 px-2 py-1 rounded text-xs font-medium">
                  {result.source}
                </div>
                {result.date && (
                  <div className="absolute top-2 right-2 bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-2 py-1 rounded text-xs font-medium">
                    {result.date}
                  </div>
                )}
              </div>
              
              <div className="p-4">
                <h2 className="font-semibold text-lg mb-1 line-clamp-2" title={result.title}>
                  {result.title}
                </h2>
                
                <div className="flex justify-between items-center mb-3">
                  <div className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                    {result.currency} {result.price.toFixed(2)}
                  </div>
                  
                  {result.location && (
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {result.location}
                    </div>
                  )}
                </div>
                
                {result.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                    {result.description}
                  </p>
                )}
                
                {/* Image text extraction - Always show this section */}
                <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center mb-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                    </svg>
                    <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400">Text from postcard:</span>
                  </div>
                  <div className="text-sm text-gray-700 dark:text-gray-300 italic">
                    {/* Front image text */}
                    <div className="mb-2">
                      <span className="font-medium text-xs mr-1">Front:</span>
                      {renderExtractedText(standardizeTextDisplay(result.image_text))}
                    </div>
                    
                    {/* Back/Additional image text */}
                    {result.additional_images && result.additional_images.length > 0 && (
                      <div className="mb-2">
                        <span className="font-medium text-xs mr-1">Back:</span>
                        {renderExtractedText(standardizeTextDisplay(
                          result.additional_image_text && result.additional_image_text.length > 0 
                            ? result.additional_image_text[0] 
                            : undefined
                        ))}
                      </div>
                    )}
                    
                    {/* Additional images beyond front/back */}
                    {result.additional_image_text && result.additional_image_text.length > 1 && (
                      result.additional_image_text.slice(1).map((text, index) => (
                        <div key={index + 1} className="mb-2">
                          <span className="font-medium text-xs mr-1">Additional {index + 2}:</span>
                          {renderExtractedText(standardizeTextDisplay(text))}
                        </div>
                      ))
                    )}
                  </div>
                </div>
                
                <a
                  href={result.affiliate_link || result.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full text-center bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded transition duration-200"
                >
                  View on {result.source}
                </a>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 dark:bg-slate-800 rounded-lg">
          <h2 className="text-xl font-semibold mb-2">No results found</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Try adjusting your search terms or filters
          </p>
          <Link href="/" className="btn-primary inline-block">
            Back to Home
          </Link>
        </div>
      )}
      
      {/* Pagination */}
      {total > 0 && (
        <div className="mt-8 flex justify-center">
          <nav className="flex items-center gap-2">
            {page > 1 && (
              <Link
                href={`/search?query=${encodeURIComponent(query)}&page=${page - 1}${yearMin ? `&year_min=${yearMin}` : ''}${yearMax ? `&year_max=${yearMax}` : ''}${location ? `&location=${encodeURIComponent(location)}` : ''}${priceMin ? `&price_min=${priceMin}` : ''}${priceMax ? `&price_max=${priceMax}` : ''}${sortBy ? `&sort_by=${sortBy}` : ''}`}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-slate-700"
              >
                Previous
              </Link>
            )}
            
            <span className="px-3 py-2 bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 font-medium rounded">
              {page}
            </span>
            
            {results.length >= 20 && (
              <Link
                href={`/search?query=${encodeURIComponent(query)}&page=${page + 1}${yearMin ? `&year_min=${yearMin}` : ''}${yearMax ? `&year_max=${yearMax}` : ''}${location ? `&location=${encodeURIComponent(location)}` : ''}${priceMin ? `&price_min=${priceMin}` : ''}${priceMax ? `&price_max=${priceMax}` : ''}${sortBy ? `&sort_by=${sortBy}` : ''}`}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-slate-700"
              >
                Next
              </Link>
            )}
          </nav>
        </div>
      )}
    </div>
  );
}