from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="PM System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PM System API is running!", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "PM System API"}

@app.get("/api/v1/test")
def test_endpoint():
    return {"message": "API is working", "test": True}

# Simple auth endpoint for testing
@app.post("/api/v1/auth/login")
def login_test(credentials: dict):
    return {
        "id": "test-user",
        "name": "Test User", 
        "email": "test@example.com",
        "token": "test-token-123"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)