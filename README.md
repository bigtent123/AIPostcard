# Postcard Search API

This is the backend API for the Postcard Search website. It's built with FastAPI and provides endpoints for searching postcards across multiple marketplaces (eBay, Etsy, HipPostcard) with AI-enhanced queries using OpenAI's GPT-4.

## Features

- **AI-Enhanced Search**: Uses GPT-4 to improve search queries for better results
- **Multi-Marketplace Integration**: Searches across eBay, Etsy, and HipPostcard
- **OCR Processing**: Extracts text from postcard images for improved search matching
- **Filtering & Sorting**: Filter by date, location, price, and sort results
- **Affiliate Integration**: Supports affiliate links for monetization

## Setup

### Prerequisites

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (for OCR functionality)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your API keys:
   ```
   cp .env.example .env
   ```

### API Keys

You'll need to obtain API keys for the following services:

- **OpenAI API**: For GPT-4 integration - [Get API Key](https://platform.openai.com/)
- **eBay API**: For eBay marketplace integration - [eBay Developers Program](https://developer.ebay.com/)
- **Etsy API**: For Etsy marketplace integration - [Etsy Developers](https://www.etsy.com/developers/)

## Running the API

### Local Development

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation

Once the server is running, you can access the auto-generated API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### AWS Lambda

The API includes Mangum integration for AWS Lambda deployment:

1. Package the application:
   ```
   pip install -r requirements.txt -t ./package
   cp -r ./app ./package/
   cd package
   zip -r ../lambda_function.zip .
   ```

2. Upload the zip file to AWS Lambda and set the handler to `app.main.handler`

### Vercel

You can also deploy to Vercel using their Python serverless functions:

1. Create a `vercel.json` file:
   ```json
   {
     "version": 2,
     "builds": [
       { "src": "app/main.py", "use": "@vercel/python" }
     ],
     "routes": [
       { "src": "/(.*)", "dest": "app/main.py" }
     ]
   }
   ```

2. Deploy using the Vercel CLI:
   ```
   vercel
   ```

## API Endpoints

### Search Postcards

- `POST /api/search` - Search for postcards with JSON request body
- `GET /api/search?query=...` - Search for postcards with query parameters

### Get Suggestions

- `GET /api/suggest?query=...` - Get search suggestions based on partial query

## Environment Variables

See `.env.example` for all required environment variables.

## License

MIT 