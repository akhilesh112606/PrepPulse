"""
RAG Pipeline for Chatbot - Handles knowledge base retrieval and augmentation
"""
import json
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Path to knowledge base
KB_PATH = Path(__file__).parent.parent / "Knowledge base"
GUARDRAILS_PATH = Path(__file__).parent.parent / "CHATBOT_GUARDRAILS.txt"


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline using SQLite for vector storage"""
    
    def __init__(self, db_path: str):
        """Initialize RAG pipeline with vector database"""
        self.db_path = db_path
        self._init_vector_db()
        self._load_knowledge_base()
        self.full_kb_content = self._load_full_knowledge_base()
        self.guardrails = self._load_guardrails()
    
    def _load_full_knowledge_base(self) -> str:
        """Load entire knowledge base as formatted text"""
        try:
            kb_text = ""
            kb_files = [
                ("course_structure.json", "📚 Courses"),
                ("assessments.json", "📝 Assessments"),
                ("certifications.json", "🏆 Certifications"),
                ("progress_tracking.json", "📊 Progress Tracking"),
                ("learning_paths.json", "🛣️  Learning Paths"),
                ("ai_enriched.json", "🤖 AI-Generated Content"),
            ]
            
            for filename, section_title in kb_files:
                kb_file = KB_PATH / filename
                if kb_file.exists():
                    with open(kb_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    kb_text += f"\n\n{'='*60}\n{section_title}\n{'='*60}\n"
                    kb_text += json.dumps(data, indent=2)
            
            print(f"✅ [RAG] Full knowledge base loaded: {len(kb_text)} characters")
            return kb_text
        except Exception as e:
            logger.error(f"Error loading full knowledge base: {str(e)}")
            print(f"❌ [RAG] Error loading full KB: {str(e)}")
            return ""
    
    def _load_guardrails(self) -> str:
        """Load chatbot guardrails from text file"""
        try:
            if GUARDRAILS_PATH.exists():
                with open(GUARDRAILS_PATH, "r", encoding="utf-8") as f:
                    guardrails = f.read()
                print(f"✅ [RAG] Chatbot guardrails loaded: {len(guardrails)} characters")
                return guardrails
            else:
                logger.warning(f"Guardrails file not found: {GUARDRAILS_PATH}")
                print(f"⚠️  [RAG] Guardrails file not found")
                return ""
        except Exception as e:
            logger.error(f"Error loading guardrails: {str(e)}")
            print(f"❌ [RAG] Error loading guardrails: {str(e)}")
            return ""
    
    def _init_vector_db(self):
        """Initialize SQLite vector database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create vector storage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vector (
                id INTEGER PRIMARY KEY,
                source_file TEXT NOT NULL,
                content_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                embedding_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster searches
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_file 
            ON vector(source_file)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_type 
            ON vector(content_type)
        """)
        
        conn.commit()
        conn.close()
    
    def _load_knowledge_base(self):
        """Load and process all knowledge base JSON files"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if KB already loaded
            cursor.execute("SELECT COUNT(*) FROM vector")
            if cursor.fetchone()[0] > 0:
                logger.info("Knowledge base already loaded")
                conn.close()
                return
            
            kb_files = [
                ("course_structure.json", "courses"),
                ("assessments.json", "assessments"),
                ("certifications.json", "certifications"),
                ("progress_tracking.json", "progress_tracking"),
                ("learning_paths.json", "learning_paths"),
                ("ai_enriched.json", "ai_enriched"),
            ]
            
            for filename, content_type in kb_files:
                kb_file = KB_PATH / filename
                if not kb_file.exists():
                    logger.warning(f"Knowledge base file not found: {kb_file}")
                    continue
                
                with open(kb_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self._process_kb_file(cursor, filename, content_type, data)
            
            conn.commit()
            conn.close()
            logger.info("Knowledge base loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
    
    def _process_kb_file(self, cursor, filename: str, content_type: str, data: Dict[str, Any]):
        """Process and store knowledge base file content"""
        try:
            if content_type == "courses":
                for course in data.get("courses", []):
                    self._store_embedding(
                        cursor,
                        filename,
                        course.get("id", ""),
                        "course",
                        course.get("title", ""),
                        json.dumps(course)
                    )
            
            elif content_type == "assessments":
                for assessment in data.get("assessments", []):
                    self._store_embedding(
                        cursor,
                        filename,
                        assessment.get("assessment_id", ""),
                        "assessment",
                        assessment.get("title", ""),
                        json.dumps(assessment)
                    )
            
            elif content_type == "certifications":
                for cert in data.get("certifications", []):
                    self._store_embedding(
                        cursor,
                        filename,
                        cert.get("certification_id", ""),
                        "certification",
                        cert.get("title", ""),
                        json.dumps(cert)
                    )
            
            elif content_type == "progress_tracking":
                self._store_embedding(
                    cursor,
                    filename,
                    "progress_tracking",
                    "system_feature",
                    "Progress Tracking System",
                    json.dumps(data.get("progress_tracking", {}))
                )
            
            elif content_type == "learning_paths":
                for path in data.get("learning_paths", []):
                    self._store_embedding(
                        cursor,
                        filename,
                        path.get("path_id", ""),
                        "learning_path",
                        path.get("title", ""),
                        json.dumps(path)
                    )
            
            elif content_type == "ai_enriched":
                # Load AI-generated courses
                for course in data.get("ai_generated_courses", []):
                    self._store_embedding(
                        cursor,
                        filename,
                        course.get("id", ""),
                        "course",
                        course.get("title", ""),
                        json.dumps(course)
                    )
                # Load AI-generated assessments
                for assessment in data.get("ai_generated_assessments", []):
                    self._store_embedding(
                        cursor,
                        filename,
                        assessment.get("assessment_id", ""),
                        "assessment",
                        assessment.get("title", ""),
                        json.dumps(assessment)
                    )
                # Load AI-generated certifications
                for cert in data.get("ai_generated_certifications", []):
                    self._store_embedding(
                        cursor,
                        filename,
                        cert.get("certification_id", ""),
                        "certification",
                        cert.get("title", ""),
                        json.dumps(cert)
                    )
                # Load AI-generated learning paths
                for path in data.get("ai_generated_learning_paths", []):
                    self._store_embedding(
                        cursor,
                        filename,
                        path.get("path_id", ""),
                        "learning_path",
                        path.get("title", ""),
                        json.dumps(path)
                    )
        
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
    
    def _store_embedding(self, cursor, source_file: str, content_id: str, 
                        content_type: str, title: str, content: str):
        """Store embedding in vector database"""
        try:
            cursor.execute("""
                INSERT INTO vector 
                (source_file, content_id, content_type, title, content, embedding_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (source_file, content_id, content_type, title, content, title))
        except Exception as e:
            logger.error(f"Error storing embedding: {str(e)}")
    
    def retrieve_relevant_context(self, user_query: str, top_k: int = 5) -> str:
        """
        Retrieve relevant knowledge base content based on user query
        Uses simple keyword matching and content type relevance
        """
        try:
            print(f"\n🔍 [RAG] Starting context retrieval for query: '{user_query}'")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query_lower = user_query.lower()
            keywords = query_lower.split()
            
            # Find relevant content using keyword matching
            placeholders = ",".join(["?" for _ in keywords])
            search_query = f"""
                SELECT content_id, content_type, title, content 
                FROM vector
                WHERE title LIKE ? OR content LIKE ?
                LIMIT ?
            """
            
            search_pattern = f"%{' '.join(keywords[:3])}%"
            cursor.execute(search_query, (search_pattern, search_pattern, top_k))
            results = cursor.fetchall()
            
            conn.close()
            
            if not results:
                print(f"❌ [RAG] No relevant context found in vector database")
                return ""
            
            # Format retrieved content
            context_parts = []
            print(f"✅ [RAG] Found {len(results)} relevant knowledge base entries")
            for content_id, content_type, title, content in results:
                try:
                    content_dict = json.loads(content)
                    formatted = self._format_context(content_type, title, content_dict)
                    context_parts.append(formatted)
                    print(f"   📌 Retrieved: {title} [{content_type}]")
                except json.JSONDecodeError:
                    context_parts.append(f"{title}: {content[:200]}...")
            
            final_context = "\n".join(context_parts)
            print(f"📤 [RAG] Context prepared and ready for LLM augmentation\n")
            return final_context
        
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return ""
    
    def _format_context(self, content_type: str, title: str, content: Dict[str, Any]) -> str:
        """Format retrieved content for LLM context"""
        if content_type == "course":
            duration = content.get("duration_hours", "N/A")
            level = content.get("level", "N/A")
            instructor = content.get("instructor", "N/A")
            return f"💼 Course: {title} (Level: {level}, Duration: {duration}h, Instructor: {instructor})"
        
        elif content_type == "assessment":
            assessment_type = content.get("type", "quiz")
            difficulty = content.get("difficulty", "N/A")
            return f"📝 Assessment: {title} (Type: {assessment_type}, Difficulty: {difficulty})"
        
        elif content_type == "certification":
            skills = ", ".join(content.get("skills_covered", [])[:3])
            return f"🏆 Certification: {title} (Skills: {skills}...)"
        
        elif content_type == "learning_path":
            duration = content.get("estimated_duration_weeks", "N/A")
            courses_count = len(content.get("courses", []))
            return f"🎯 Learning Path: {title} ({courses_count} courses, {duration} weeks)"
        
        elif content_type == "system_feature":
            return f"ℹ️ System Feature: {title}"
        
        else:
            return f"📚 {title}"
    
    def search_and_enrich_with_openai(self, user_query: str, openai_client) -> str:
        """
        Search vector DB first, if not found, use OpenAI to generate info and store it
        This makes the KB self-learning!
        
        Args:
            user_query: User's search query
            openai_client: OpenAI client instance
        
        Returns: Relevant content as text
        """
        try:
            print(f"\n🔍 [RAG+AI] Smart context retrieval for: '{user_query}'")
            
            # Step 1: Try to find in vector database
            vector_results = self.retrieve_relevant_context(user_query, top_k=3)
            
            if vector_results and len(vector_results.strip()) > 50:
                print(f"✅ [RAG+AI] Found in vector database, returning cached content")
                return vector_results
            
            # Step 2: Not found in vector DB, query OpenAI
            print(f"🤖 [RAG+AI] Content not in KB, querying OpenAI for information...")
            
            enrichment_prompt = f"""
Given the user's query: "{user_query}"

Please provide detailed information in the following JSON format:
{{
    "type": "course",
    "title": "Exact title from the query",
    "description": "A detailed 2-3 sentence description of the topic",
    "duration_hours": 40,
    "level": "Beginner/Intermediate/Advanced",
    "instructor": "Likely instructor or 'Expert Instructor'",
    "key_topics": ["Topic 1", "Topic 2", "Topic 3"],
    "learning_outcomes": ["Outcome 1", "Outcome 2"]
}}

Respond with ONLY valid JSON, no markdown, no extra text.
"""
            
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator. Provide structured course information as JSON."
                    },
                    {
                        "role": "user",
                        "content": enrichment_prompt
                    }
                ],
                temperature=0.7
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            # Step 3: Parse OpenAI response
            try:
                course_data = json.loads(response_text)
                print(f"✅ [RAG+AI] OpenAI generated course: {course_data.get('title', 'Unknown')}")
                
                # Step 4: Store in vector database
                self._store_ai_generated_content(course_data)
                
                # Step 5: Format and return
                formatted = f"""
💼 **NEW COURSE DISCOVERED & ADDED TO KB**

Title: {course_data.get('title', 'N/A')}
Level: {course_data.get('level', 'N/A')}
Duration: {course_data.get('duration_hours', 'N/A')} hours
Instructor: {course_data.get('instructor', 'N/A')}

Description:
{course_data.get('description', 'N/A')}

Key Topics:
{chr(10).join(['• ' + str(t) for t in course_data.get('key_topics', [])])}

Learning Outcomes:
{chr(10).join(['✓ ' + str(o) for o in course_data.get('learning_outcomes', [])])}

📌 This course information was generated and stored in our knowledge base!
"""
                
                print(f"📤 [RAG+AI] Content enriched and stored successfully")
                return formatted
            
            except json.JSONDecodeError:
                print(f"⚠️  [RAG+AI] Failed to parse OpenAI response as JSON")
                print(f"   Response was: {response_text[:200]}")
                # Return raw response if JSON parsing fails
                return f"ℹ️  Information from AI:\n\n{response_text}"
        
        except Exception as e:
            logger.error(f"Error in search and enrich: {str(e)}")
            print(f"❌ [RAG+AI] Error: {str(e)}")
            return ""
    
    def _store_ai_generated_content(self, course_data: Dict[str, Any]):
        """Store AI-generated course info in vector database AND ai_enriched.json file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate ID
            cursor.execute("SELECT MAX(CAST(SUBSTR(content_id, -3) AS INTEGER)) FROM vector WHERE content_id LIKE 'AI_%'")
            result = cursor.fetchone()[0]
            next_id = (result or 0) + 1
            content_id = f"AI_{next_id:03d}"
            
            content_type = course_data.get("type", "course")
            
            # Store in vector database
            cursor.execute("""
                INSERT INTO vector 
                (source_file, content_id, content_type, title, content, embedding_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "ai_enriched.json",
                content_id,
                content_type,
                course_data.get("title", ""),
                json.dumps(course_data),
                course_data.get("title", "")
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ [RAG+AI] Stored in vector DB with ID: {content_id}")
            
            # STEP 2: Persist to ai_enriched.json file
            self._persist_to_ai_enriched_json(course_data, content_id, content_type)
        
        except Exception as e:
            logger.error(f"Error storing AI content: {str(e)}")
            print(f"❌ [RAG+AI] Error storing: {str(e)}")
    
    def _persist_to_ai_enriched_json(self, course_data: Dict[str, Any], content_id: str, content_type: str):
        """Persist AI-generated content to ai_enriched.json file"""
        try:
            ai_enriched_file = KB_PATH / "ai_enriched.json"
            
            # Load existing content
            if ai_enriched_file.exists():
                with open(ai_enriched_file, "r", encoding="utf-8") as f:
                    ai_data = json.load(f)
            else:
                # Initialize structure if file doesn't exist
                ai_data = {
                    "metadata": {
                        "file_name": "ai_enriched.json",
                        "description": "AI-generated and OpenAI-enriched knowledge base content",
                        "version": "1.0"
                    },
                    "ai_generated_courses": [],
                    "ai_generated_assessments": [],
                    "ai_generated_certifications": [],
                    "ai_generated_learning_paths": [],
                    "metadata_tracking": {
                        "total_ai_entries": 0,
                        "entries_by_type": {"course": 0, "assessment": 0, "certification": 0, "learning_path": 0},
                        "auto_generated_ids": {"next_course_id": 1, "next_assessment_id": 1, "next_certification_id": 1, "next_learning_path_id": 1}
                    }
                }
            
            # Add content ID to the course data for JSON storage
            course_data_with_id = course_data.copy()
            course_data_with_id["id"] = content_id
            course_data_with_id["generated_at"] = str(Path.cwd())  # Add metadata
            
            # Append to appropriate section based on type
            if content_type == "course":
                ai_data["ai_generated_courses"].append(course_data_with_id)
                ai_data["metadata_tracking"]["entries_by_type"]["course"] += 1
            elif content_type == "assessment":
                ai_data["ai_generated_assessments"].append(course_data_with_id)
                ai_data["metadata_tracking"]["entries_by_type"]["assessment"] += 1
            elif content_type == "certification":
                ai_data["ai_generated_certifications"].append(course_data_with_id)
                ai_data["metadata_tracking"]["entries_by_type"]["certification"] += 1
            elif content_type == "learning_path":
                ai_data["ai_generated_learning_paths"].append(course_data_with_id)
                ai_data["metadata_tracking"]["entries_by_type"]["learning_path"] += 1
            
            # Update metadata
            ai_data["metadata"]["last_updated"] = str(Path.cwd())
            ai_data["metadata_tracking"]["total_ai_entries"] += 1
            
            # Write back to file
            with open(ai_enriched_file, "w", encoding="utf-8") as f:
                json.dump(ai_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ [RAG+AI] Persisted to ai_enriched.json (Total entries: {ai_data['metadata_tracking']['total_ai_entries']})")
        
        except Exception as e:
            logger.error(f"Error persisting to ai_enriched.json: {str(e)}")
            print(f"⚠️  [RAG+AI] Warning: Could not save to JSON file: {str(e)}")
    
    def preprocess_query_for_rag(self, user_query: str) -> Tuple[str, str]:
        """
        Preprocess user query and return relevant knowledge base content
        Returns (processed_query, relevant_content_or_empty_string)
        
        If no relevant content found, returns empty string to trigger OpenAI fallback
        """
        try:
            query_lower = user_query.lower()
            
            # Detect query intent for logging
            relevant_types = []
            if any(word in query_lower for word in ["course", "learn", "study", "module", "bootcamp"]):
                relevant_types.append("courses")
            if any(word in query_lower for word in ["test", "quiz", "exam", "assessment"]):
                relevant_types.append("assessments")
            if any(word in query_lower for word in ["certificate", "credential", "badge"]):
                relevant_types.append("certifications")
            if any(word in query_lower for word in ["progress", "track", "complete"]):
                relevant_types.append("progress_tracking")
            if any(word in query_lower for word in ["path", "roadmap", "journey", "plan"]):
                relevant_types.append("learning_paths")
            
            intent_label = f"[{', '.join(relevant_types)}]" if relevant_types else "[general]"
            print(f"🎯 [RAG] Query intent detected: {intent_label}")
            
            # Search for SPECIFIC relevant content matching the query
            print(f"🔍 [RAG] Searching for specific content matching: '{user_query}'")
            relevant_context = self.retrieve_relevant_context(user_query, top_k=5)
            
            # If we found specific content, return it
            if relevant_context and len(relevant_context.strip()) > 50:
                print(f"✅ [RAG] Found specific matching content in knowledge base")
                return user_query, relevant_context
            else:
                # No specific content found - return empty to trigger OpenAI enrichment
                print(f"❌ [RAG] No specific matching content found - will search OpenAI")
                return user_query, ""
        
        except Exception as e:
            logger.error(f"Error preprocessing query: {str(e)}")
            print(f"❌ [RAG] Error: {str(e)}")
            return user_query, ""
    
    def get_full_knowledge_base_for_llm(self) -> str:
        """
        Return the complete knowledge base content formatted for LLM inclusion in system prompt
        This provides the LLM with ALL available information from the knowledge base
        """
        try:
            print(f"📚 [RAG] Preparing complete knowledge base for LLM system prompt...")
            return self.full_kb_content
        except Exception as e:
            logger.error(f"Error getting KB for LLM: {str(e)}")
            return ""
    
    def get_guardrails_for_llm(self) -> str:
        """
        Return the chatbot guardrails for LLM system prompt
        These restrictions prevent the LLM from violating ethical guidelines
        """
        try:
            if self.guardrails:
                print(f"🛡️  [RAG] Attaching chatbot guardrails to LLM system prompt...")
                return self.guardrails
            else:
                return ""
        except Exception as e:
            logger.error(f"Error getting guardrails for LLM: {str(e)}")
            return ""


def get_rag_pipeline(database_path: str) -> RAGPipeline:
    """
    Get or create RAG pipeline instance
    """
    global _rag_instance
    if '_rag_instance' not in globals():
        _rag_instance = RAGPipeline(database_path)
    return _rag_instance
