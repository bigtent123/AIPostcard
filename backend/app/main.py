from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os

from app.api import search, suggest

# Initialize FastAPI app
app = FastAPI(
    title="Postcard Search API",
    description="API for searching postcards across multiple marketplaces with AI-enhanced queries",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Local Next.js development server
    "http://localhost:3001",  # Alternative port
    "http://localhost:3002",  # Alternative port
    "http://localhost:3003",  # Alternative port
    "http://localhost:3004",  # Alternative port
    "http://localhost:3005",  # Alternative port
    "http://localhost:3020",  # Frontend port from restart script
    "http://localhost:3021",  # New frontend port
    "http://localhost:8080",  # Backend port
    "http://localhost:9000",  # Backend port
    "http://localhost:9001",  # Backend port from restart script
    "https://postcard-search.netlify.app",  # Production frontend URL (update this)
    "*",  # For development - remove in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(suggest.router, prefix="/api", tags=["suggest"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Postcard Search API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify the API is running"""
    return {"status": "healthy", "version": "1.0"}

# Handler for AWS Lambda
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 9002))
    print(f"Starting server on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True) 