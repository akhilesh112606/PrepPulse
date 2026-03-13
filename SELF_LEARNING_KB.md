# Self-Learning Knowledge Base with OpenAI Fallback

## Overview

Your Vprep platform now has an intelligent, **self-learning knowledge base** that automatically discovers and stores missing content via OpenAI integration. When users ask about courses/certifications/assessments not in your vector database, the system:

1. **Searches Vector DB** for existing content
2. **Queries OpenAI** if not found
3. **Stores the response** in vector database
4. **Caches for future** queries (instant responses)

This ensures your platform never says "I don't know" while continuously expanding the knowledge base.

---

## How It Works

### 🔄 Complete Flow

```
User Question
    ↓
Search Vector Database
    ↓
┌─────────────────────────────────────┐
│ Is Content Found?                   │
└─────────────────────────────────────┘
    ↓
    ├─ YES → Return from cache ✅ (instant)
    │
    └─ NO → Query OpenAI 🤖
             ↓
          Parse Response
             ↓
          Store in Vector DB 💾
             ↓
          Return to User 📤
             ↓
      Next Query → Vector DB ✅ (instant)
```

### 📊 Time & Cost Comparison

**Without Self-Learning:**
```
Query 1: "Tell me about Python 100 Days" 
         → "I don't have that course"
Query 2: "Tell me about Python 100 Days"
         → "I don't have that course" (repeated)
```

**With Self-Learning:**
```
Query 1: "Tell me about Python 100 Days"
         → OpenAI search + store (3-5 sec)
         → Returns: "NEW COURSE DISCOVERED"
Query 2: "Tell me about Python 100 Days"
         → Vector DB lookup (instant)
         → Returns: Complete course info
```

**Cost Savings:**
- First query: 1 OpenAI API call
- All subsequent queries: 0 API calls (cached)
- If 100 users ask about same course:
  - Without caching: 100 OpenAI calls
  - With caching: 1 OpenAI call + 99 instant lookups
  - **Savings: 99% reduction in API costs!**

---

## Technical Implementation

### 1. New Method: `search_and_enrich_with_openai()`

**Location:** `app/rag_pipeline.py` (RAGPipeline class)

**What it does:**
```python
def search_and_enrich_with_openai(self, user_query: str, openai_client):
    # Step 1: Search vector database
    # Step 2: If not found, query OpenAI
    # Step 3: Parse structured response
    # Step 4: Store in vector database
    # Step 5: Return formatted content
```

**OpenAI Prompt Structure:**
```
Given user query: "Tell me about Python 100 Days"

Return ONLY this JSON:
{
    "type": "course",
    "title": "...",
    "description": "...",
    "duration_hours": 40,
    "level": "Intermediate",
    "instructor": "Expert Instructor",
    "key_topics": [...],
    "learning_outcomes": [...]
}
```

### 2. Modified Function: `_invoke_chat_response()`

**Location:** `app/routes.py`

**New Logic:**
```python
def _invoke_chat_response(...):
    # Get from KB first
    kb_context = rag_pipeline.preprocess_query_for_rag(user_message)
    
    # If insufficient, use OpenAI fallback
    if len(kb_context) < 100:
        rag_context = rag_pipeline.search_and_enrich_with_openai(
            user_message, 
            openai_client
        )
    else:
        rag_context = kb_context
    
    # Return augmented response with OpenAI-discovered content
```

### 3. Storage: `_store_ai_generated_content()`

**What it stores:**
- Type: course/certification/assessment
- Source: ai_enriched.json
- ID: Auto-generated (AI_001, AI_002, etc.)
- Content: Full structured data
- Timestamp: Auto-added by SQLite

**Database Query:**
```sql
INSERT INTO vector 
(source_file, content_id, content_type, title, content, embedding_summary)
VALUES ('ai_enriched.json', 'AI_001', 'course', 'Python 100 Days', {...}, 'Python 100 Days')
```

---

## Example Dialogue

### **User Input:**
```
"Can you explain the Python 100 Day Course?"
```

### **System Process:**

**Step 1: Search Vector DB**
```
🔍 [RAG+AI] Smart context retrieval for: 'Python 100 Day Course'
```

**Step 2: Not Found → Query OpenAI**
```
🤖 [RAG+AI] Content not in KB, querying OpenAI for information...
```

**Step 3: Parse OpenAI Response**
```
✅ [RAG+AI] OpenAI generated course: Python 100 Days Challenge
```

**Step 4: Store in Vector DB**
```
✅ [RAG+AI] Stored in vector DB with ID: AI_001
```

**Step 5: Return to User**
```
💼 **NEW COURSE DISCOVERED & ADDED TO KB**

Title: Python 100 Days Challenge
Level: Intermediate
Duration: 100 hours
Instructor: Expert Instructor

Description:
A comprehensive 100-day journey...

Key Topics:
• Python fundamentals
• Object-oriented programming
• Data structures
• Web development

Learning Outcomes:
✓ Master Python programming
✓ Build real-world applications
✓ Solve complex problems

📌 This course information was generated and stored in our knowledge base!
```

### **AI Logs Show:**
```
✅ [CHATBOT] RAG context augmented to LLM system prompt (length: 1245 chars)
🤖 [CHATBOT] Sending augmented prompt to GPT-4o-mini LLM...
✨ [CHATBOT] LLM response generated successfully
```

---

## Usage Scenarios

### Scenario 1: Brand New Course Request
```
User: "Do you have IBM Cloud certification?"
System: [Not in KB] → Query OpenAI → Store → Return info
Result: Instant response about IBM Cloud cert
```

### Scenario 2: Repeated Query (Cached)
```
User: "Tell me more about IBM Cloud certification"
System: [Found in Vector DB] → Return from cache
Result: Instant response (no OpenAI call)
```

### Scenario 3: Related Topic
```
User: "What about AWS certification?"
System: [Not in KB] → Query OpenAI → Store → Return info
Result: New content discovered and cached
```

---

## Configuration & Control

### Threshold for OpenAI Fallback
**Location:** `app/routes.py` line ~91

**Current Setting:**
```python
if not kb_context or len(kb_context.strip()) < 100:
    rag_context = rag_pipeline.search_and_enrich_with_openai(...)
```

**Meaning:** If KB content is less than 100 characters, use OpenAI

**To Adjust:**
```python
# More aggressive (use OpenAI more often)
if len(kb_context.strip()) < 500:  # Higher threshold

# Less aggressive (use OpenAI rarely)
if len(kb_context.strip()) < 50:   # Lower threshold

# Disable OpenAI fallback completely
# if False:  # Comment out entirely
```

---

## Monitor & Debug

### Terminal Logs Show Everything:

**When KB content found (instant):**
```
✅ [RAG+AI] Found in vector database, returning cached content
```

**When OpenAI is queried:**
```
🤖 [RAG+AI] Content not in KB, querying OpenAI for information...
✅ [RAG+AI] OpenAI generated course: [Title]
✅ [RAG+AI] Stored in vector DB with ID: AI_001
```

### Check KB Growth:
```bash
curl http://localhost:5000/api/kb/status
```

Returns:
```json
{
  "success": true,
  "status": {
    "total_courses": 5,      // Original
    "total_assessments": 8,
    "total_certifications": 3,
    "last_updated": "2026-02-28T10:30:45"
  }
}
```

### Search for AI-Discovered Content:
```bash
curl "http://localhost:5000/api/kb/search?q=python%20100%20days"
```

---

## Best Practices

✅ **Monitor Cost:** Check OpenAI API usage in console logs  
✅ **Cache Hit Rate:** More repeats = better cache efficiency  
✅ **Manual Review:** Periodically check AI-generated content quality  
✅ **Backup KB:** Regularly backup `data/preppulse.db`  
✅ **Threshold Tuning:** Adjust KB content threshold based on need  

---

## Limitations & Fine-Tuning

### Current Limitations:
1. ❌ No manual review of AI-generated content
2. ❌ All OpenAI responses assumed correct
3. ❌ No duplicate detection between AI-gen and manual content
4. ❌ No update mechanism (re-query for refreshed info)

### Future Enhancements:
1. ✅ Manual approval workflow for AI-generated content
2. ✅ Semantic deduplication (detect similar courses)
3. ✅ Content expiration & refresh
4. ✅ User feedback on AI-generated courses
5. ✅ Cost tracking & optimization
6. ✅ A/B testing different OpenAI prompts

---

## Troubleshooting

### "OpenAI API Error"
```
❌ [RAG+AI] Error querying OpenAI
Make sure:
1. OPENAI_API_KEY env var is set
2. API key is valid
3. Account has available credits
4. Model "gpt-4o-mini" is available
```

### "Failed to parse OpenAI response"
```
❌ [RAG+AI] Failed to parse OpenAI response as JSON
Cause: OpenAI returned non-JSON response
Fix: Check OpenAI prompt is clear for JSON output
```

### "Content stored but not searchable"
```
1. Check it was actually stored:
   SELECT COUNT(*) FROM vector WHERE source_file = 'ai_enriched.json';
2. Verify vector table exists:
   SELECT * FROM vector LIMIT 5;
3. Check search keywords match:
   curl "...?q=exact_title"
```

---

## Testing the Feature

### Test 1: Manual Integration Test
```bash
# Terminal 1
python run.py

# Terminal 2
python test_self_learning_kb.py
```

### Test 2: Live Chat Testing
1. Open `http://localhost:5000` in browser
2. Ask about a course NOT in Knowledge Base folder
3. Example: "Tell me about Docker Mastery course"
4. Watch terminal for logs:
   - 🔍 searching...
   - 🤖 querying OpenAI...
   - ✅ storing...
5. Check KB status increased
6. Ask same question again → instant response

### Test 3: Database Verification
```bash
# Check AI-generated entries
sqlite3 data/preppulse.db "SELECT title, content_type FROM vector WHERE source_file='ai_enriched.json';"
```

---

## API Response Examples

### Successful AI Enrichment Response:
```json
{
  "chatbot_response": "💼 **NEW COURSE DISCOVERED & ADDED TO KB**\n\nTitle: Python 100 Days Challenge\n...",
  "source": "OpenAI",
  "cached": false,
  "storage_id": "AI_001"
}
```

### Cache Hit Response:
```json
{
  "chatbot_response": "💼 Course: Python 100 Days Challenge...",
  "source": "Vector Database",
  "cached": true,
  "duration_ms": 15
}
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        CHATBOT REQUEST                           │
└──────────────────────────────────────────────────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  Search Vector DB    │
                    └──────────────────────┘
                               ↓
        ┌──────────────────────────────────────────────┐
        │       Is Content Found & Sufficient?        │
        └──────────────────────────────────────────────┘
                        ↓               ↓
                       YES              NO
                        ↓               ↓
                    [CACHE]        [OPEN AI]
                        ↓               ↓
                    <100ms         [PARSE]
                        ↓               ↓
                        │       [STORE IN DB]
                        │               ↓
                        ←───────────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Augment LLM Prompt   │
                    └──────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  GPT-4o-mini LLM     │
                    └──────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │   User Response      │
                    └──────────────────────┘
```

---

## Summary

Your Vprep platform now has:

✅ **Intelligent Fallback** - Never stuck with "I don't know"  
✅ **Automatic Learning** - KB grows with each unique query  
✅ **Smart Caching** - Fast responses for repeated topics  
✅ **Seamless Integration** - Works within existing RAG pipeline  
✅ **Cost Optimization** - Minimal API calls after first query  
✅ **Scalable KB** - Grows to match user interests  

**Every user interaction makes your knowledge base smarter! 🚀**
