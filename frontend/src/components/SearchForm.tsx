'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

interface SearchFormProps {
  initialQuery: string;
}

export function SearchForm({ initialQuery }: SearchFormProps) {
  const [query, setQuery] = useState(initialQuery);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  
  // Create a ref for the search form container
  const searchContainerRef = useRef<HTMLDivElement>(null);

  // Handle clicks outside the search component
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        searchContainerRef.current && 
        !searchContainerRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    }
    
    // Add event listener when suggestions are shown
    if (showSuggestions) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    
    // Clean up the event listener
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSuggestions]);

  // Fetch suggestions as the user types
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length < 2) {
        setSuggestions([]);
        return;
      }

      setIsLoading(true);
      try {
        // API endpoint
        const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'}/api/suggest?query=${encodeURIComponent(query)}`;
        
        // Make the request with proper error handling
        const response = await fetch(apiUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          mode: 'cors',
        });
        
        if (response.ok) {
          const data = await response.json();
          setSuggestions(data.suggestions || []);
        } else {
          console.error('Error fetching suggestions:', response.statusText);
          setSuggestions([]);
          
          // Generate mock suggestions for development
          generateMockSuggestions();
        }
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions([]);
        
        // Generate mock suggestions for development
        generateMockSuggestions();
      } finally {
        setIsLoading(false);
      }
    };

    // Debounce the API call
    const timeoutId = setTimeout(() => {
      fetchSuggestions();
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);
  
  // Generate mock suggestions for development
  const generateMockSuggestions = () => {
    if (query.length < 2) return;
    
    const mockSuggestions = [
      `${query} vintage postcards`,
      `${query} antique postcards`,
      `${query} 1950s postcards`,
      `${query} black and white postcards`,
      `${query} color postcards`
    ];
    
    setSuggestions(mockSuggestions);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?query=${encodeURIComponent(query.trim())}`);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    router.push(`/search?query=${encodeURIComponent(suggestion)}`);
    setShowSuggestions(false);
  };

  return (
    <div className="relative" ref={searchContainerRef}>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-grow">
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            placeholder="Search for vintage postcards (e.g., 'Paris 1920s')"
            className="search-input"
            aria-label="Search query"
          />
          {isLoading && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
            </div>
          )}
        </div>
        <button type="submit" className="btn-primary sm:w-auto w-full">
          Search
        </button>
      </form>

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div 
          className="absolute z-10 w-full bg-white dark:bg-slate-800 mt-1 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
          onMouseDown={(e) => e.preventDefault()} // Prevent blur event from hiding suggestions before click
        >
          <ul>
            {suggestions.map((suggestion, index) => (
              <li 
                key={index}
                className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-slate-700 cursor-pointer"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 