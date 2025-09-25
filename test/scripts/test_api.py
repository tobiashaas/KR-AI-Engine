from fastapi import FastAPI
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="KRAI Test API")

@app.get("/")
async def root():
    return {"message": "KRAI Test API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "KRAI Test API is running"}

@app.get("/test-db")
async def test_db():
    try:
        # Test database connection
        conn = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
            port=int(os.getenv("POSTGRES_PORT", "54322")),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            database=os.getenv("POSTGRES_DB", "postgres")
        )
        
        # Test query
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        
        return {
            "status": "success",
            "message": "Database connection successful",
            "test_query_result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }

@app.get("/test-supabase")
async def test_supabase():
    try:
        supabase_url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
        return {
            "status": "success",
            "message": "Supabase configuration loaded",
            "supabase_url": supabase_url
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Supabase configuration error: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
