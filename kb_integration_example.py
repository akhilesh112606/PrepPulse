"""
Knowledge Base Integration Example
Shows how to integrate KB refinement with the chatbot
"""

from app.kb_manager import get_kb_manager
from app.rag_pipeline import get_rag_pipeline


def handle_missing_content_in_chat(user_query: str, db_path: str) -> tuple:
    """
    Check if user is asking about content not in KB
    If missing, return suggestion to add it
    
    Returns: (has_content, response_message)
    """
    kb_manager = get_kb_manager(db_path)
    
    # Keywords indicating user wants specific content
    content_keywords = {
        "course": ["course", "learn", "tutorial", "training"],
        "assessment": ["quiz", "test", "exam", "assessment"],
        "certification": ["certificate", "credential", "certification"]
    }
    
    # Search for relevant content
    results = kb_manager.search_knowledge_base(user_query)
    
    if results:
        # Content found in KB
        return True, f"Found {len(results)} relevant items in our knowledge base"
    
    # Check if user is asking about something that should exist
    query_lower = user_query.lower()
    
    # Detect what type of content user is asking about
    content_type = None
    for ctype, keywords in content_keywords.items():
        if any(kw in query_lower for kw in keywords):
            content_type = ctype
            break
    
    if content_type:
        # User is asking about specific content type that's not in KB
        return False, (
            f"I don't have a {content_type} about '{user_query}' in my knowledge base yet. "
            f"Would you like me to add it? "
            f"Please provide details like: title, description, level/difficulty, duration, and key topics."
        )
    
    # Generic missing content message
    return False, (
        "I don't have information about that in my knowledge base. "
        "Would you like to help me add this content? "
        "Please provide relevant details."
    )


def suggest_kb_addition(user_query: str, chatbot_response: str, db_path: str) -> str:
    """
    If chatbot couldn't answer from KB, suggest adding the content
    Call this after chatbot gives a generic response
    """
    kb_manager = get_kb_manager(db_path)
    
    # Check if content is in KB
    results = kb_manager.search_knowledge_base(user_query)
    
    if not results and len(chatbot_response) < 200:  # Generic response
        suggestion = (
            "\n\n💡 **Note:** I don't have detailed information about this in my knowledge base. "
            "If this is important course material, administrators can add it using our KB refinement system. "
            "New courses, certifications, and assessments can be added via API or directly to the knowledge base."
        )
        return chatbot_response + suggestion
    
    return chatbot_response


def extract_kb_addition_request(user_input: str, content_type: str, db_path: str) -> dict:
    """
    Extract course/assessment/certification details from user input
    Helps parse user's natural language into structured data
    
    Example:
    user_input = "Add a course called Advanced Python, taught by Dr. Smith, 40 hours, intermediate level"
    content_type = "course"
    
    Returns: dict with parsed fields ready for add_course()
    """
    import re
    
    data = {}
    input_lower = user_input.lower()
    
    # Extract title (often in quotes or after "course" keyword)
    title_match = re.search(r'(?:course|called|named)\s+["\']?([^"\'.,;]+)["\']?', input_lower)
    if title_match:
        data['title'] = title_match.group(1).strip().title()
    
    # Extract instructor/author
    instructor_match = re.search(r'(?:by|taught by|instructor|author)[:\s]+([A-Za-z\s]+?)(?:[,.]|$)', input_lower)
    if instructor_match:
        data['instructor'] = instructor_match.group(1).strip().title()
    
    # Extract duration
    duration_match = re.search(r'(\d+)\s*(?:hours?|weeks?|months?)', input_lower)
    if duration_match:
        hours = int(duration_match.group(1))
        if 'week' in input_lower:
            hours = hours * 7 * 5  # Estimate hours from weeks
        elif 'month' in input_lower:
            hours = hours * 30 * 5
        data['duration_hours'] = hours if content_type == 'course' else None
    
    # Extract level/difficulty
    levels = ['beginner', 'intermediate', 'advanced', 'easy', 'medium', 'hard']
    for level in levels:
        if level in input_lower:
            if content_type == 'course':
                # Map to Level format
                if level in ['beginner', 'easy']:
                    data['level'] = 'Beginner'
                elif level in ['intermediate', 'medium']:
                    data['level'] = 'Intermediate'
                else:
                    data['level'] = 'Advanced'
            else:
                data['difficulty'] = level.capitalize()
            break
    
    return data


# ============================================================================
# EXAMPLE USAGE IN CHATBOT FLOW
# ============================================================================

def example_chatbot_integration(user_message: str, db_path: str, client) -> str:
    """
    Example of how to integrate KB refinement into main chatbot flow
    """
    from app.rag_pipeline import get_rag_pipeline
    
    # Step 1: Check if content is missing from KB
    has_content, kb_status = handle_missing_content_in_chat(user_message, db_path)
    
    if has_content:
        print(f"📚 KB Status: {kb_status}")
        # Content exists, proceed with normal RAG-augmented response
        rag_pipeline = get_rag_pipeline(db_path)
        _, rag_context = rag_pipeline.preprocess_query_for_rag(user_message)
        # ... normal chatbot flow ...
    else:
        print(f"⚠️  Missing KB content: {kb_status}")
        # Suggest adding content
        # Option 1: Return suggestion message
        # Option 2: Provide LLM with OK to add and parse details
    
    return kb_status


# ============================================================================
# BATCH INITIALIZATION EXAMPLE
# ============================================================================

def initialize_kb_with_courses(db_path: str):
    """
    Example: Bulk add initial course content
    Useful for setting up the knowledge base from scratch
    """
    kb_manager = get_kb_manager(db_path)
    
    courses = [
        {
            "title": "Full Stack Web Development",
            "description": "Build modern web applications with frontend and backend technologies",
            "duration_hours": 80,
            "level": "Intermediate",
            "instructor": "Mr. Web Developer"
        },
        {
            "title": "Cloud Deployment with AWS",
            "description": "Deploy and scale applications on AWS cloud platform",
            "duration_hours": 50,
            "level": "Intermediate",
            "instructor": "Ms. Cloud Architect"
        },
        {
            "title": "AI and Deep Learning",
            "description": "Build neural networks and deep learning models using TensorFlow",
            "duration_hours": 70,
            "level": "Advanced",
            "instructor": "Dr. AI Researcher"
        }
    ]
    
    print("🚀 Initializing Knowledge Base with courses...")
    for course in courses:
        success = kb_manager.add_course(course)
        if success:
            print(f"   ✅ {course['title']}")
        else:
            print(f"   ⚠️  {course['title']} (may already exist)")
    
    # Show final status
    status = kb_manager.get_kb_status()
    print(f"\n✨ KB Initialization Complete!")
    print(f"   Total Courses: {status['total_courses']}")
    print(f"   Total Assessments: {status['total_assessments']}")
    print(f"   Total Certifications: {status['total_certifications']}")
    print(f"   Last Updated: {status['last_updated']}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "data/preppulse.db"
    
    print("💡 KB Integration Examples")
    print("=" * 60)
    
    # Example 1: Initialize KB with courses
    print("\n1️⃣ Bulk Initialize Knowledge Base")
    print("-" * 60)
    initialize_kb_with_courses(db_path)
    
    # Example 2: Check for missing content
    print("\n\n2️⃣ Check Missing Content")
    print("-" * 60)
    test_queries = [
        "Do you have a GraphQL course?",
        "I want to learn Data Science",
        "Is there a Python certification?"
    ]
    
    for query in test_queries:
        has_content, message = handle_missing_content_in_chat(query, db_path)
        print(f"Query: {query}")
        print(f"Status: {'✅ Found' if has_content else '❌ Missing'}")
        print(f"Message: {message}\n")
