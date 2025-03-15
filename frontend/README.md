# Postcard Search Frontend

This is the frontend for the Postcard Search website. It's built with Next.js and provides a user interface for searching postcards across multiple marketplaces.

## Features

- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Server-Side Rendering**: Fast initial loads and SEO-friendly pages
- **AI-Enhanced Search**: Integration with backend API for AI-powered search
- **Advanced Filtering**: Filter by date, location, price, and more
- **Infinite Scrolling**: Load more results as you scroll

## Setup

### Prerequisites

- Node.js 18.x or later
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   # or
   yarn install
   ```
3. Create a `.env.local` file with your API URL:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## Development

Run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Building for Production

```bash
npm run build
# or
yarn build
```

## Deployment

This project is configured for easy deployment on Netlify:

1. Push your code to a Git repository
2. Connect the repository to Netlify
3. Set the build command to `npm run build` and the publish directory to `out`
4. Set the environment variable `NEXT_PUBLIC_API_URL` to your backend API URL

## Project Structure

- `src/app/page.tsx` - Home page
- `src/app/search/page.tsx` - Search results page
- `src/components/` - Reusable components
  - `SearchForm.tsx` - Search input with suggestions
  - `SearchResults.tsx` - Display search results
  - `FilterPanel.tsx` - Filters for search results
  - `SearchSkeleton.tsx` - Loading skeleton for search results

## Environment Variables

- `NEXT_PUBLIC_API_URL` - URL of the backend API

## License

MIT
