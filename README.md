# Postcard Search Website

A full-stack web application for searching vintage postcards across multiple marketplaces with AI-enhanced queries.

## Project Overview

This project consists of two main components:

1. **Frontend**: A Next.js React application that provides a modern, responsive user interface for searching postcards.
2. **Backend**: A FastAPI Python application that integrates with marketplace APIs and uses OpenAI's GPT-4 for query enhancement.

## Features

- **AI-Enhanced Search**: Uses GPT-4 to improve search queries for better results
- **Multi-Marketplace Integration**: Searches across eBay, Etsy, and HipPostcard
- **OCR Processing**: Extracts text from postcard images for improved search matching
- **Filtering & Sorting**: Filter by date, location, price, and sort results
- **Responsive Design**: Works on desktop and mobile devices
- **Server-Side Rendering**: Fast initial loads and SEO-friendly pages
- **Affiliate Integration**: Supports affiliate links for monetization

## Architecture

- **Frontend**: Next.js, React, Tailwind CSS
- **Backend**: FastAPI, Python, OpenAI API
- **Deployment**: Netlify (frontend), AWS Lambda/Vercel (backend)
- **Data Flow**: Real-time API calls to marketplaces, no database required

## Getting Started

### Prerequisites

- Node.js 18.x or later
- Python 3.8 or later
- API keys for OpenAI, eBay, and Etsy

### Setup

1. Clone the repository
2. Set up the backend:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Then edit .env with your API keys
   ```
3. Set up the frontend:
   ```
   cd frontend
   npm install
   cp .env.example .env.local  # Then edit .env.local with your API URL
   ```

### Running Locally

1. Start the backend:
   ```
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn app.main:app --reload
   ```
2. Start the frontend:
   ```
   cd frontend
   npm run dev
   ```
3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment

### Backend Deployment

The backend includes Mangum integration for AWS Lambda deployment and can also be deployed to Vercel as a serverless function.

### Frontend Deployment

The frontend is configured for easy deployment on Netlify.

## License

MIT

## Acknowledgements

- OpenAI for GPT-4 API
- eBay Developer Program
- Etsy API
- HipPostcard 