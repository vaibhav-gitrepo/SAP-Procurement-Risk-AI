import os
import pandas as pd
from sqlalchemy import create_engine

def ingest():
    try:
        url = os.getenv("DATABASE_URL")
        if not url:
            print("❌ No DATABASE_URL found in .env")
            return
            
        
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
            
        print("📡 Attempting to connect to Render...")
        # Added connect_args for a 10-second timeout so it doesn't hang forever
        engine = create_engine(url, connect_args={'connect_timeout': 10})
        
        # Test connection
        with engine.connect() as conn:
            print("🔗 Connection successful!")
           
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    ingest()