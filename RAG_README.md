# RAG (Retrieval-Augmented Generation) Pipeline for Vprep Chatbot

## Overview

The RAG pipeline integrates your knowledge base with the chatbot, allowing it to provide context-aware responses based on course structures, assessments, certifications, progress tracking, and learning paths.

## Architecture

```
User Query
    ↓
[RAG Pipeline]
    ├── Knowledge Base Loading (JSON files)
    ├── Vector Database (SQLite)
    ├── Query Preprocessing & Intent Detection
    └── Relevant Context Retrieval
         ↓
[Augmented System Prompt]
    ├── System Instructions
    ├── Retrieved Knowledge Base Context
    └── User Provided Context
         ↓
[OpenAI GPT-4o-mini]
    ↓
[Chat Response]
```

## Knowledge Base Structure

The RAG pipeline processes 5 knowledge base files:

### 1. **Course Structure** (`course_structure.json`)
- Course metadata (ID, title, level, duration)
- Module and lesson hierarchy
- Content types (video, interactive, etc.)
- Instructor information

### 2. **Assessments** (`assessments.json`)
- Quiz, coding assignment, project, and exam definitions
- Difficulty levels and passing scores
- Time limits and evaluation criteria
- Test cases and rubrics

### 3. **Certifications** (`certifications.json`)
- Certification requirements and prerequisites
- Skills covered by each certification
- Validity periods and badges
- Parent-child relationships for advanced certs

### 4. **Progress Tracking** (`progress_tracking.json`)
- Metrics definitions (completion %, velocity, engagement)
- Tracking components and statuses
- Visualization options
- Daily, weekly, monthly reporting

### 5. **Learning Paths** (`learning_paths.json`)
- Predefined learning journeys
- Course sequencing and prerequisites
- Difficulty progression
- Success rates and estimated duration

## Components

### RAGPipeline Class (`app/rag_pipeline.py`)

**Methods:**

#### `__init__(db_path: str)`
Initialize the RAG pipeline with SQLite vector database.

```python
from app.rag_pipeline import get_rag_pipeline

rag = get_rag_pipeline(database_path)
```

#### `retrieve_relevant_context(user_query: str, top_k: int = 5) -> str`
Retrieve top-k most relevant knowledge base entries based on user query using keyword matching.

```python
context = rag.retrieve_relevant_context("How do I structure my learning?")
```

#### `preprocess_query_for_rag(user_query: str) -> Tuple[str, str]`
Preprocess query, detect intent, and return augmented context.

```python
query, context = rag.preprocess_query_for_rag(user_message)
```

### Database Schema

**Table: `vector`**
```sql
CREATE TABLE vector (
    id INTEGER PRIMARY KEY,
    source_file TEXT NOT NULL,           -- Which KB file this came from
    content_id TEXT NOT NULL,             -- Unique ID within content
    content_type TEXT NOT NULL,           -- Type: course, assessment, etc.
    title TEXT,                           -- Content title
    content TEXT NOT NULL,                -- Full JSON content
    embedding_summary TEXT,               -- Summary for retrieval
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Integration with Chatbot

The RAG pipeline is automatically integrated into the `/chat` endpoint:

```python
@main.route("/chat", methods=["POST"])
def chat():
    # User sends message
    user_message = payload.get("message")
    
    # RAG retrieves relevant knowledge base content
    # System prompt is augmented with context
    reply = _invoke_chat_response(
        client, 
        user_message, 
        context_text,
        database_path=current_app.config.get("DATABASE")
    )
    
    # Return augmented response
```

## Setup Instructions

### 1. Initialize RAG Vector Database

Run the initialization script to populate the vector database:

```bash
python init_rag.py data/preppulse.db
```

Or from the Flask application context:

```python
from app.rag_pipeline import get_rag_pipeline

rag = get_rag_pipeline("data/preppulse.db")
```

### 2. Verify Installation

Check that knowledge base is loaded:

```bash
sqlite3 data/preppulse.db "SELECT COUNT(*) FROM vector;"
```

Expected output: Number of KB entries (typically 50+)

## Query Examples

### Course Query
**User:** "What courses are available?"
**Retrieved:** Course metadata, duration, level, instructor

### Assessment Query
**User:** "How do I take a quiz?"
**Retrieved:** Assessment types, difficulty, time limits

### Certification Query
**User:** "What do I need for a certification?"
**Retrieved:** Cert requirements, skills covered, prerequisites

### Learning Path Query
**User:** "Create a learning plan for web development"
**Retrieved:** Web Development pathway, courses, milestones

## Performance Optimization

### Keyword Matching Strategy
- Uses simple keyword matching (case-insensitive)
- Splits user query into keywords
- Searches title and content fields
- Returns top-k most relevant entries

### Caching
- RAG instance is cached globally to avoid reinitializing on every request
- Vector database is persistent in SQLite

### Future Enhancements
- Semantic similarity using embeddings (OpenAI API)
- Cosine similarity for better relevance matching
- Caching of popular queries
- Hierarchical knowledge organization

## Troubleshooting

### Issue: Knowledge base not loading

**Solution:** 
- Verify KB files exist in `Knowledge base/` directory
- Check file permissions and JSON format
- Run `python init_rag.py` to reinitialize

### Issue: Chatbot not using KB context

**Solution:**
- Ensure database path is passed to `_invoke_chat_response()`
- Check Flask app configuration for DATABASE setting
- Verify RAG pipeline initialized without errors

### Issue: Slow retrieval

**Solution:**
- Check SQLite indexes are created
- Run VACUUM on database to optimize
- Consider reducing top_k parameter

## Example Usage

```python
# Initialize RAG
from app.rag_pipeline import get_rag_pipeline

rag = get_rag_pipeline("data/preppulse.db")

# Retrieve context for a query
query = "How to learn web development?"
context = rag.retrieve_relevant_context(query, top_k=5)

# Output context
print(context)
# 💼 Course: Web Development Fundamentals (Level: Intermediate, Duration: 60h...)
# 🎯 Learning Path: Modern Web Development (2 courses, 16 weeks)
# ...

# Preprocess query with intent detection
query, aug_context = rag.preprocess_query_for_rag(query)
```

## Features

✅ **Knowledge Base Integration** - All KB data indexed and retrievable
✅ **Intent Detection** - Automatically detects query type (course, cert, path, etc.)
✅ **Context Formatting** - Structured output with emojis for readability
✅ **SQLite Vector DB** - Lightweight, no external dependencies
✅ **Caching** - RAG instance cached for performance
✅ **Error Handling** - Graceful fallback if KB unavailable

## Next Steps

1. **Test the chatbot** with KB-aware queries
2. **Monitor retrieval performance** and adjust top_k
3. **Add semantic embeddings** for better relevance (optional)
4. **Extend KB** with additional courses, paths, and certifications
5. **Fine-tune system prompt** based on user feedback
