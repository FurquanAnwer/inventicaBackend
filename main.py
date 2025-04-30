
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()

app = FastAPI(title="News Search API")

# CORS configuration 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://inventica-frontend.vercel.app"],  # frontend URL
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Getting Serper API key from environment variables
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/news"

if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY environment variable is not set")


@app.get("/search")
async def search_news(name: str):
    """
    Search for news articles related to a person's name using Serper.dev API.
    
    Args:
        name: The name of the person to search for
        
    Returns:
        Dictionary containing search results
    """
    if not name or name.strip() == "":
        raise HTTPException(status_code=400, detail="Name parameter cannot be empty")
    
    try:
        
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        
        
        payload = {
            "q": f"{name} news",
            "num": 20  # Number of results to return
        }
        
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SERPER_URL,
                headers=headers,
                json=payload,
                timeout=10.0
            )
            
        # Check if response is successful
        response.raise_for_status()
        
        # Return processed results
        return response.json()
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from Serper API: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to Serper API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "News Search API is running"}


# Run with: uvicorn main:app --reload
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)