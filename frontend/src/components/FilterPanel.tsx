'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface FilterPanelProps {
  query: string;
  yearMin?: number;
  yearMax?: number;
  location?: string;
  priceMin?: number;
  priceMax?: number;
  sortBy?: string;
}

export function FilterPanel({
  query,
  yearMin,
  yearMax,
  location,
  priceMin,
  priceMax,
  sortBy = 'relevance'
}: FilterPanelProps) {
  const router = useRouter();
  
  // Local state for filter values
  const [yearMinValue, setYearMinValue] = useState<string>(yearMin?.toString() || '');
  const [yearMaxValue, setYearMaxValue] = useState<string>(yearMax?.toString() || '');
  const [locationValue, setLocationValue] = useState<string>(location || '');
  const [priceMinValue, setPriceMinValue] = useState<string>(priceMin?.toString() || '');
  const [priceMaxValue, setPriceMaxValue] = useState<string>(priceMax?.toString() || '');
  const [sortByValue, setSortByValue] = useState<string>(sortBy);
  
  // Apply filters
  const applyFilters = () => {
    // Build query string
    const params = new URLSearchParams();
    params.set('query', query);
    
    if (yearMinValue) params.set('year_min', yearMinValue);
    if (yearMaxValue) params.set('year_max', yearMaxValue);
    if (locationValue) params.set('location', locationValue);
    if (priceMinValue) params.set('price_min', priceMinValue);
    if (priceMaxValue) params.set('price_max', priceMaxValue);
    if (sortByValue) params.set('sort_by', sortByValue);
    
    // Navigate to the new URL with filters
    router.push(`/search?${params.toString()}`);
  };
  
  // Reset filters
  const resetFilters = () => {
    setYearMinValue('');
    setYearMaxValue('');
    setLocationValue('');
    setPriceMinValue('');
    setPriceMaxValue('');
    setSortByValue('relevance');
    
    // Navigate to the URL with only the query
    router.push(`/search?query=${encodeURIComponent(query)}`);
  };
  
  // Handle sort change
  const handleSortChange = (value: string) => {
    setSortByValue(value);
    
    // Apply sort immediately
    const params = new URLSearchParams();
    params.set('query', query);
    
    if (yearMinValue) params.set('year_min', yearMinValue);
    if (yearMaxValue) params.set('year_max', yearMaxValue);
    if (locationValue) params.set('location', locationValue);
    if (priceMinValue) params.set('price_min', priceMinValue);
    if (priceMaxValue) params.set('price_max', priceMaxValue);
    params.set('sort_by', value);
    
    router.push(`/search?${params.toString()}`);
  };
  
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold mb-4">Filters</h2>
      
      {/* Year Range */}
      <div className="mb-4">
        <h3 className="font-medium mb-2">Year</h3>
        <div className="flex gap-2">
          <input
            type="number"
            placeholder="Min"
            value={yearMinValue}
            onChange={(e) => setYearMinValue(e.target.value)}
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded"
            min="1800"
            max="2023"
          />
          <input
            type="number"
            placeholder="Max"
            value={yearMaxValue}
            onChange={(e) => setYearMaxValue(e.target.value)}
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded"
            min="1800"
            max="2023"
          />
        </div>
      </div>
      
      {/* Location */}
      <div className="mb-4">
        <h3 className="font-medium mb-2">Location</h3>
        <input
          type="text"
          placeholder="e.g., Paris, New York"
          value={locationValue}
          onChange={(e) => setLocationValue(e.target.value)}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded"
        />
      </div>
      
      {/* Price Range */}
      <div className="mb-4">
        <h3 className="font-medium mb-2">Price ($)</h3>
        <div className="flex gap-2">
          <input
            type="number"
            placeholder="Min"
            value={priceMinValue}
            onChange={(e) => setPriceMinValue(e.target.value)}
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded"
            min="0"
            step="0.01"
          />
          <input
            type="number"
            placeholder="Max"
            value={priceMaxValue}
            onChange={(e) => setPriceMaxValue(e.target.value)}
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded"
            min="0"
            step="0.01"
          />
        </div>
      </div>
      
      {/* Sort By */}
      <div className="mb-6">
        <h3 className="font-medium mb-2">Sort By</h3>
        <select
          value={sortByValue}
          onChange={(e) => handleSortChange(e.target.value)}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-slate-700"
        >
          <option value="relevance">Relevance</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="newest">Newest</option>
        </select>
      </div>
      
      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={applyFilters}
          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded"
        >
          Apply
        </button>
        <button
          onClick={resetFilters}
          className="flex-1 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-medium py-2 px-4 rounded"
        >
          Reset
        </button>
      </div>
      
      {/* Active Filters */}
      {(yearMinValue || yearMaxValue || locationValue || priceMinValue || priceMaxValue) && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <h3 className="font-medium mb-2">Active Filters:</h3>
          <div className="flex flex-wrap">
            {yearMinValue && (
              <span className="filter-chip filter-chip-active">
                Year Min: {yearMinValue}
              </span>
            )}
            {yearMaxValue && (
              <span className="filter-chip filter-chip-active">
                Year Max: {yearMaxValue}
              </span>
            )}
            {locationValue && (
              <span className="filter-chip filter-chip-active">
                Location: {locationValue}
              </span>
            )}
            {priceMinValue && (
              <span className="filter-chip filter-chip-active">
                Price Min: ${priceMinValue}
              </span>
            )}
            {priceMaxValue && (
              <span className="filter-chip filter-chip-active">
                Price Max: ${priceMaxValue}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 