import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("app/static", exist_ok=True)
    os.makedirs("app/templates", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 