import { Suspense } from 'react';
import { SearchResults } from '@/components/SearchResults';
import { SearchForm } from '@/components/SearchForm';
import { FilterPanel } from '@/components/FilterPanel';
import { SearchSkeleton } from '@/components/SearchSkeleton';

// This is a Server Component
export default async function SearchPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  // Await searchParams to comply with Next.js 15 requirements
  const params = await Promise.resolve(searchParams);
  
  const query = typeof params.query === 'string' ? params.query : '';
  const page = typeof params.page === 'string' ? parseInt(params.page) : 1;
  const yearMin = typeof params.year_min === 'string' ? parseInt(params.year_min) : undefined;
  const yearMax = typeof params.year_max === 'string' ? parseInt(params.year_max) : undefined;
  const location = typeof params.location === 'string' ? params.location : undefined;
  const priceMin = typeof params.price_min === 'string' ? parseFloat(params.price_min) : undefined;
  const priceMax = typeof params.price_max === 'string' ? parseFloat(params.price_max) : undefined;
  const sortBy = typeof params.sort_by === 'string' ? params.sort_by : 'relevance';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <SearchForm initialQuery={query} />
      </div>

      {query ? (
        <div className="flex flex-col md:flex-row gap-8">
          {/* Filters sidebar */}
          <div className="md:w-64 flex-shrink-0">
            <FilterPanel 
              query={query}
              yearMin={yearMin}
              yearMax={yearMax}
              location={location}
              priceMin={priceMin}
              priceMax={priceMax}
              sortBy={sortBy}
            />
          </div>

          {/* Search results */}
          <div className="flex-grow">
            <Suspense fallback={<SearchSkeleton />}>
              <SearchResults 
                query={query}
                page={page}
                yearMin={yearMin}
                yearMax={yearMax}
                location={location}
                priceMin={priceMin}
                priceMax={priceMax}
                sortBy={sortBy}
              />
            </Suspense>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <h2 className="text-2xl font-semibold mb-4">Enter a search term to find postcards</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Search for vintage postcards by location, time period, or subject matter
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
            <div className="p-4 bg-gray-50 dark:bg-slate-800 rounded-lg">
              <p className="font-medium">Try searching for:</p>
              <ul className="mt-2 text-indigo-600 dark:text-indigo-400">
                <li>"Paris 1900s"</li>
                <li>"New York skyline"</li>
                <li>"Vintage Chicago"</li>
              </ul>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-slate-800 rounded-lg">
              <p className="font-medium">Search by era:</p>
              <ul className="mt-2 text-indigo-600 dark:text-indigo-400">
                <li>"Victorian postcards"</li>
                <li>"1950s Florida"</li>
                <li>"Art Deco postcards"</li>
              </ul>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-slate-800 rounded-lg">
              <p className="font-medium">Search by type:</p>
              <ul className="mt-2 text-indigo-600 dark:text-indigo-400">
                <li>"Linen postcards"</li>
                <li>"Real photo postcards"</li>
                <li>"Holiday postcards"</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 