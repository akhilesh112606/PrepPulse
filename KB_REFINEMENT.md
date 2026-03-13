# Knowledge Base Refinement System

## Overview

The Knowledge Base Refinement System allows you to dynamically add and update learning content (courses, assessments, certifications) to your platform without modifying the original JSON files manually. New data is automatically persisted to the knowledge base files and integrated into the RAG pipeline for LLM augmentation.

## Features

✅ **Add New Courses** - Add courses with duration, level, instructor, and modules  
✅ **Add Assessments** - Create quizzes, coding tests, exams, and projects  
✅ **Add Certifications** - Define certification programs with skills and requirements  
✅ **Search Knowledge Base** - Find existing content by keyword  
✅ **Track Updates** - Monitor KB statistics and last update times  
✅ **Auto-Persist** - Changes automatically saved to JSON files  
✅ **Vector DB Sync** - New entries automatically added to RAG pipeline  

---

## API Endpoints

### 1. Add a New Course

**Endpoint:** `POST /api/kb/add-course`

**Request Body:**
```json
{
  "title": "Advanced Python Programming",
  "description": "Master advanced Python concepts and best practices",
  "duration_hours": 45,
  "level": "Advanced",
  "instructor": "Prof. Jane Smith",
  "modules": [
    {
      "module_id": "MOD_ADV001",
      "title": "Decorators and Metaclasses",
      "lessons": []
    }
  ]
}
```

**Fields:**
- `title` (string, **required**) - Course name
- `description` (string, **required**) - Course description
- `duration_hours` (integer, **required**) - Total course duration in hours
- `level` (string, **required**) - Beginner/Intermediate/Advanced
- `instructor` (string, **required**) - Instructor name
- `modules` (array, optional) - Course modules and lessons

**Response (201):**
```json
{
  "success": true,
  "message": "Course 'Advanced Python Programming' added successfully"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/kb/add-course \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Python Programming",
    "description": "Master advanced Python concepts",
    "duration_hours": 45,
    "level": "Advanced",
    "instructor": "Prof. Jane Smith"
  }'
```

---

### 2. Add a New Assessment

**Endpoint:** `POST /api/kb/add-assessment`

**Request Body:**
```json
{
  "title": "Python Advanced Practices Quiz",
  "description": "Quiz covering decorators, metaclasses, and async programming",
  "type": "quiz",
  "difficulty": "Hard",
  "questions": [
    {
      "question_id": "Q1",
      "text": "What is a metaclass in Python?",
      "options": ["A class of classes", "A type of inheritance", "A design pattern"],
      "correct_answer": "A class of classes"
    }
  ],
  "duration_minutes": 45
}
```

**Fields:**
- `title` (string, **required**) - Assessment name
- `description` (string, **required**) - Assessment description
- `type` (string, **required**) - quiz/coding/exam/project
- `difficulty` (string, **required**) - Easy/Medium/Hard
- `questions` (array, optional) - Quiz questions
- `duration_minutes` (integer, optional) - Time limit in minutes

**Response (201):**
```json
{
  "success": true,
  "message": "Assessment 'Python Advanced Practices Quiz' added successfully"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/kb/add-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Advanced Test",
    "description": "Test your Python knowledge",
    "type": "exam",
    "difficulty": "Hard"
  }'
```

---

### 3. Add a New Certification

**Endpoint:** `POST /api/kb/add-certification`

**Request Body:**
```json
{
  "title": "AWS Solutions Architect Associate",
  "description": "Learn to design scalable AWS architectures",
  "duration_weeks": 12,
  "skills_covered": [
    "EC2 Management",
    "RDS Database Design",
    "S3 Storage Solutions",
    "VPC Networking",
    "IAM Security"
  ],
  "requirements": {
    "prerequisites": "Basic cloud knowledge",
    "exam_fee": 150,
    "passing_score": 720
  },
  "issuing_body": "Amazon Web Services"
}
```

**Fields:**
- `title` (string, **required**) - Certification name
- `description` (string, **required**) - Certification description
- `duration_weeks` (integer, **required**) - Duration in weeks
- `skills_covered` (array, optional) - List of skills covered
- `requirements` (object, optional) - Prerequisites, fees, passing scores
- `issuing_body` (string, optional) - Issuing organization (default: Vprep)

**Response (201):**
```json
{
  "success": true,
  "message": "Certification 'AWS Solutions Architect Associate' added successfully"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/kb/add-certification \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Google Cloud Professional",
    "description": "Master Google Cloud Platform",
    "duration_weeks": 8,
    "skills_covered": ["GCP services", "Cloud Architecture"]
  }'
```

---

### 4. Search Knowledge Base

**Endpoint:** `GET /api/kb/search?q=<query>`

**Query Parameters:**
- `q` (string, **required**) - Search keyword

**Response (200):**
```json
{
  "query": "python",
  "total_results": 3,
  "results": [
    {
      "type": "course",
      "title": "Advanced Python Programming",
      "data": { ...full course data... }
    },
    {
      "type": "assessment",
      "title": "Python Advanced Practices Quiz",
      "data": { ...full assessment data... }
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/kb/search?q=python
```

**JavaScript Example:**
```javascript
async function searchKB(query) {
  const response = await fetch(`/api/kb/search?q=${encodeURIComponent(query)}`);
  const data = await response.json();
  console.log(`Found ${data.total_results} results:`, data.results);
}

searchKB("data science");
```

---

### 5. Get Knowledge Base Status

**Endpoint:** `GET /api/kb/status`

**Response (200):**
```json
{
  "success": true,
  "status": {
    "total_courses": 5,
    "total_assessments": 8,
    "total_certifications": 3,
    "last_updated": "2026-02-28T10:30:45.123456"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/kb/status
```

---

## Python Usage Examples

### Using the KBManager Directly

```python
from app.kb_manager import get_kb_manager

# Initialize KB manager
kb_manager = get_kb_manager("data/preppulse.db")

# Add a new course
course = {
    "title": "Mobile App Development",
    "description": "Build cross-platform mobile apps with React Native",
    "duration_hours": 50,
    "level": "Intermediate",
    "instructor": "Alex Mobile",
    "modules": []
}
kb_manager.add_course(course)

# Add a new assessment
assessment = {
    "title": "React Native Project",
    "description": "Build a complete mobile app",
    "type": "project",
    "difficulty": "Medium",
    "questions": [],
    "duration_minutes": 480
}
kb_manager.add_assessment(assessment)

# Search knowledge base
results = kb_manager.search_knowledge_base("mobile")
for result in results:
    print(f"Found {result['type']}: {result['title']}")

# Get KB status
status = kb_manager.get_kb_status()
print(f"Total courses: {status['total_courses']}")
print(f"Last updated: {status['last_updated']}")
```

---

## Workflow: Adding Content When Not Found

### Scenario
User asks: **"Do you have a course on Machine Learning with Scikit-learn?"**

The chatbot should:

1. **Search the KB** for "machine learning scikit-learn"
2. **If not found** → Return to user: "I don't have that course yet. Would you like me to add it?"
3. **User confirms** → Provides course details
4. **System adds** → Course is inserted and available for future queries

### Implementation

```python
from app.kb_manager import get_kb_manager

def handle_missing_content(user_query: str, kb_manager):
    """Check if content exists, if not, offer to add it"""
    
    # Search KB
    results = kb_manager.search_knowledge_base(user_query)
    
    if results:
        return f"Found {len(results)} results in our knowledge base!"
    else:
        return (
            "I don't have information about that in my knowledge base yet. "
            "Would you like to add this new course/content? "
            "Please provide: title, description, duration, level, and instructor."
        )
```

---

## Auto-Update Trigger Example

```python
# Integration with RAG pipeline
from app.kb_manager import get_kb_manager
from app.rag_pipeline import get_rag_pipeline

def update_kb_from_user_request(user_input: str, db_path: str):
    """
    If user mentions new content not in KB, prompt to add it
    """
    kb_manager = get_kb_manager(db_path)
    rag_pipeline = get_rag_pipeline(db_path)
    
    # Search existing KB
    search_terms = [word for word in user_input.split() if len(word) > 3]
    results = kb_manager.search_knowledge_base(" ".join(search_terms))
    
    if not results and any(word in user_input.lower() for word in ["course", "certification", "assessment"]):
        print(f"🔔 New content detected: {user_input}")
        print("Consider adding this to the knowledge base")
        return True
    
    return False
```

---

## Knowledge Base File Structure

After adding content, the JSON files are automatically updated:

**Knowledge base/course_structure.json:**
```json
{
  "courses": [
    {...existing courses...},
    {
      "id": "COURSE_004",
      "title": "New Course",
      "description": "...",
      "duration_hours": 40,
      "level": "Intermediate",
      "instructor": "Dr. New",
      "modules": []
    }
  ],
  "metadata": {
    "total_courses": 4,
    "last_updated": "2026-02-28T10:30:45.123456",
    "version": "1.0"
  }
}
```

---

## Best Practices

✅ **Validate** content before adding to KB  
✅ **Check duplicates** - System prevents duplicate titles  
✅ **Use consistent naming** - Follow existing title/naming conventions  
✅ **Fill all required fields** - Don't leave gaps in course data  
✅ **Add to RAG immediately** - New content available to LLM right away  
✅ **Monitor KB growth** - Use `/api/kb/status` to track size  

---

## Error Handling

**Duplicate Content:**
```json
{
  "success": false,
  "message": "Failed to add course or course already exists"
}
```

**Missing Fields:**
```json
{
  "error": "Missing required fields: title, description, duration_hours"
}
```

**Database Error:**
```json
{
  "error": "Database connection failed"
}
```

---

## Future Enhancements

🔮 **Semantic Deduplication** - Use embeddings to detect similar content  
🔮 **Bulk Import** - Add multiple courses at once from CSV  
🔮 **Auto-Categorization** - AI-powered content categorization  
🔮 **Version Control** - Track KB changes over time  
🔮 **User Contributions** - Allow users to suggest new content  

---

## Support & Troubleshooting

**Q: New course not appearing in responses?**  
A: Run `/api/kb/status` to verify it was added, then test with `/api/kb/search`

**Q: How to update existing course?**  
A: Currently, delete and re-add. Future enhancement will support updates.

**Q: Can I import from CSV?**  
A: Not yet - use the API endpoints to add courses one by one, or use Python script with KBManager directly.
