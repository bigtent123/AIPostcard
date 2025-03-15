import Link from 'next/link';
import Image from 'next/image';

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-indigo-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">
              Find Vintage Postcards Across Multiple Marketplaces
            </h1>
            <p className="text-xl md:text-2xl max-w-3xl mx-auto mb-8 text-indigo-100">
              Search eBay, Etsy, and HipPostcard all at once with our AI-enhanced search
            </p>
            
            {/* Search Form */}
            <div className="max-w-2xl mx-auto">
              <form 
                action="/search" 
                method="get"
                className="flex flex-col md:flex-row gap-3"
              >
                <input
                  type="text"
                  name="query"
                  placeholder="Search for vintage postcards (e.g., 'Paris 1920s')"
                  className="search-input flex-grow"
                  required
                />
                <button type="submit" className="btn-primary md:w-auto w-full">
                  Search
                </button>
              </form>
              
              <div className="mt-4 text-sm text-indigo-200">
                Try: 
                <Link href="/search?query=New York 1950s" className="ml-2 underline">New York 1950s</Link>,
                <Link href="/search?query=vintage Paris Eiffel Tower" className="ml-2 underline">vintage Paris Eiffel Tower</Link>,
                <Link href="/search?query=Chicago World's Fair" className="ml-2 underline">Chicago World's Fair</Link>
              </div>
            </div>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-white dark:bg-slate-900 rounded-t-3xl"></div>
      </section>
      
      {/* Features Section */}
      <section className="py-16 bg-white dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Why Use Postcard Search?</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-indigo-100 dark:bg-indigo-900 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Search Multiple Sources</h3>
              <p className="text-gray-600 dark:text-gray-400">Find postcards from eBay, Etsy, and HipPostcard all in one search.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-indigo-100 dark:bg-indigo-900 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">AI-Enhanced Search</h3>
              <p className="text-gray-600 dark:text-gray-400">Our AI improves your search terms to find more relevant postcards.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-indigo-100 dark:bg-indigo-900 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Advanced Filtering</h3>
              <p className="text-gray-600 dark:text-gray-400">Filter by date, location, and price to find exactly what you're looking for.</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* How It Works Section */}
      <section className="py-16 bg-gray-50 dark:bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white dark:bg-slate-700 p-6 rounded-lg shadow-md">
              <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mb-4">1</div>
              <h3 className="text-xl font-semibold mb-2">Enter Your Search</h3>
              <p className="text-gray-600 dark:text-gray-300">Type what you're looking for, even in natural language like "postcards from early 20th century Paris".</p>
            </div>
            
            <div className="bg-white dark:bg-slate-700 p-6 rounded-lg shadow-md">
              <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mb-4">2</div>
              <h3 className="text-xl font-semibold mb-2">AI Enhancement</h3>
              <p className="text-gray-600 dark:text-gray-300">Our AI expands your query with relevant terms and searches across multiple marketplaces.</p>
            </div>
            
            <div className="bg-white dark:bg-slate-700 p-6 rounded-lg shadow-md">
              <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mb-4">3</div>
              <h3 className="text-xl font-semibold mb-2">Browse Results</h3>
              <p className="text-gray-600 dark:text-gray-300">View all matching postcards in one place, with filters to narrow down your search.</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-16 bg-indigo-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Find Your Perfect Postcard?</h2>
          <p className="text-xl mb-8 max-w-3xl mx-auto">Start searching now to discover vintage postcards from around the world.</p>
          <Link href="/search" className="inline-block bg-white text-indigo-600 font-semibold px-6 py-3 rounded-lg hover:bg-indigo-50 transition duration-200">
            Start Searching
          </Link>
        </div>
      </section>
    </div>
  );
}
