"""
RAG Vector Database Setup and Initialization Script
Run this to populate the vector database with knowledge base embeddings
"""
import sys
import sqlite3
from pathlib import Path

def init_rag_database(db_path: str):
    """Initialize RAG vector database with knowledge base"""
    try:
        from app.rag_pipeline import RAGPipeline
        
        print("🔄 Initializing RAG Vector Database...")
        print(f"📁 Database path: {db_path}")
        
        # Create RAG pipeline instance
        rag = RAGPipeline(db_path)
        
        # Check database status
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vector")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ RAG Vector Database initialized successfully!")
        print(f"📊 Total knowledge base entries loaded: {count}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error initializing RAG database: {str(e)}")
        return False


if __name__ == "__main__":
    # Get database path from argument or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/preppulse.db"
    init_rag_database(db_path)
