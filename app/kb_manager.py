"""
Knowledge Base Manager - Handles dynamic updates and refinements to the knowledge base
Allows adding new courses, certifications, assessments, and learning paths
"""
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

KB_PATH = Path(__file__).parent.parent / "Knowledge base"


class KBManager:
    """Manages knowledge base updates and refinements"""
    
    def __init__(self, db_path: str):
        """Initialize KB Manager"""
        self.db_path = db_path
        self.kb_path = KB_PATH
        self.ensure_kb_directory()
    
    def ensure_kb_directory(self):
        """Ensure Knowledge base directory exists"""
        self.kb_path.mkdir(parents=True, exist_ok=True)
    
    def add_course(self, course_data: Dict[str, Any]) -> bool:
        """
        Add a new course to the knowledge base
        
        Args:
            course_data: {
                'title': str,
                'description': str,
                'duration_hours': int,
                'level': str (Beginner/Intermediate/Advanced),
                'instructor': str,
                'modules': list (optional)
            }
        """
        try:
            print(f"\n📚 [KB Manager] Adding new course: {course_data.get('title', 'Unknown')}")
            
            # Load existing courses
            courses_file = self.kb_path / "course_structure.json"
            if courses_file.exists():
                with open(courses_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"courses": [], "metadata": {}}
            
            # Generate ID if not provided
            if "id" not in course_data:
                course_num = len(data.get("courses", [])) + 1
                course_data["id"] = f"COURSE_{course_num:03d}"
            
            # Ensure required fields
            course_data.setdefault("modules", [])
            course_data.setdefault("level", "Beginner")
            
            # Check for duplicates
            for course in data.get("courses", []):
                if course.get("title").lower() == course_data.get("title", "").lower():
                    print(f"⚠️  [KB Manager] Course '{course_data['title']}' already exists")
                    return False
            
            # Add new course
            data["courses"].append(course_data)
            data["metadata"]["total_courses"] = len(data["courses"])
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save back to file
            with open(courses_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ [KB Manager] Course added successfully: {course_data['id']}")
            
            # Update in database
            self._update_vector_db_course(course_data)
            
            return True
        
        except Exception as e:
            logger.error(f"Error adding course: {str(e)}")
            print(f"❌ [KB Manager] Error adding course: {str(e)}")
            return False
    
    def add_assessment(self, assessment_data: Dict[str, Any]) -> bool:
        """
        Add a new assessment to the knowledge base
        
        Args:
            assessment_data: {
                'title': str,
                'description': str,
                'type': str (quiz/coding/exam/project),
                'difficulty': str (Easy/Medium/Hard),
                'questions': list (optional),
                'duration_minutes': int (optional)
            }
        """
        try:
            print(f"\n📝 [KB Manager] Adding new assessment: {assessment_data.get('title', 'Unknown')}")
            
            # Load existing assessments
            assessments_file = self.kb_path / "assessments.json"
            if assessments_file.exists():
                with open(assessments_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"assessments": [], "metadata": {}}
            
            # Generate ID if not provided
            if "assessment_id" not in assessment_data:
                assess_num = len(data.get("assessments", [])) + 1
                assessment_data["assessment_id"] = f"ASSESS_{assess_num:03d}"
            
            # Ensure required fields
            assessment_data.setdefault("questions", [])
            assessment_data.setdefault("difficulty", "Medium")
            assessment_data.setdefault("type", "quiz")
            
            # Check for duplicates
            for assessment in data.get("assessments", []):
                if assessment.get("title").lower() == assessment_data.get("title", "").lower():
                    print(f"⚠️  [KB Manager] Assessment '{assessment_data['title']}' already exists")
                    return False
            
            # Add new assessment
            data["assessments"].append(assessment_data)
            data["metadata"]["total_assessments"] = len(data["assessments"])
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save back to file
            with open(assessments_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ [KB Manager] Assessment added successfully: {assessment_data['assessment_id']}")
            
            # Update in database
            self._update_vector_db_assessment(assessment_data)
            
            return True
        
        except Exception as e:
            logger.error(f"Error adding assessment: {str(e)}")
            print(f"❌ [KB Manager] Error adding assessment: {str(e)}")
            return False
    
    def add_certification(self, cert_data: Dict[str, Any]) -> bool:
        """
        Add a new certification to the knowledge base
        
        Args:
            cert_data: {
                'title': str,
                'description': str,
                'skills_covered': list,
                'duration_weeks': int,
                'requirements': dict,
                'issuing_body': str
            }
        """
        try:
            print(f"\n🏆 [KB Manager] Adding new certification: {cert_data.get('title', 'Unknown')}")
            
            # Load existing certifications
            certs_file = self.kb_path / "certifications.json"
            if certs_file.exists():
                with open(certs_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"certifications": [], "metadata": {}}
            
            # Generate ID if not provided
            if "certification_id" not in cert_data:
                cert_num = len(data.get("certifications", [])) + 1
                cert_data["certification_id"] = f"CERT_{cert_num:03d}"
            
            # Ensure required fields
            cert_data.setdefault("skills_covered", [])
            cert_data.setdefault("requirements", {})
            
            # Check for duplicates
            for cert in data.get("certifications", []):
                if cert.get("title").lower() == cert_data.get("title", "").lower():
                    print(f"⚠️  [KB Manager] Certification '{cert_data['title']}' already exists")
                    return False
            
            # Add new certification
            data["certifications"].append(cert_data)
            data["metadata"]["total_certifications"] = len(data["certifications"])
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save back to file
            with open(certs_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ [KB Manager] Certification added successfully: {cert_data['certification_id']}")
            
            # Update in database
            self._update_vector_db_certification(cert_data)
            
            return True
        
        except Exception as e:
            logger.error(f"Error adding certification: {str(e)}")
            print(f"❌ [KB Manager] Error adding certification: {str(e)}")
            return False
    
    def search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for matching content
        
        Returns list of matching items with type and title
        """
        try:
            results = []
            query_lower = query.lower()
            
            # Search courses
            courses_file = self.kb_path / "course_structure.json"
            if courses_file.exists():
                with open(courses_file, "r", encoding="utf-8") as f:
                    courses_data = json.load(f)
                for course in courses_data.get("courses", []):
                    if (query_lower in course.get("title", "").lower() or 
                        query_lower in course.get("description", "").lower() or
                        query_lower in course.get("instructor", "").lower()):
                        results.append({"type": "course", "title": course.get("title"), "data": course})
            
            # Search assessments
            assessments_file = self.kb_path / "assessments.json"
            if assessments_file.exists():
                with open(assessments_file, "r", encoding="utf-8") as f:
                    assessments_data = json.load(f)
                for assessment in assessments_data.get("assessments", []):
                    if (query_lower in assessment.get("title", "").lower() or 
                        query_lower in assessment.get("description", "").lower()):
                        results.append({"type": "assessment", "title": assessment.get("title"), "data": assessment})
            
            # Search certifications
            certs_file = self.kb_path / "certifications.json"
            if certs_file.exists():
                with open(certs_file, "r", encoding="utf-8") as f:
                    certs_data = json.load(f)
                for cert in certs_data.get("certifications", []):
                    if (query_lower in cert.get("title", "").lower() or 
                        query_lower in cert.get("description", "").lower()):
                        results.append({"type": "certification", "title": cert.get("title"), "data": cert})
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            print(f"❌ [KB Manager] Error searching: {str(e)}")
            return []
    
    def _update_vector_db_course(self, course_data: Dict[str, Any]):
        """Update vector database with new course"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO vector 
                (source_file, content_id, content_type, title, content, embedding_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "course_structure.json",
                course_data.get("id", ""),
                "course",
                course_data.get("title", ""),
                json.dumps(course_data),
                course_data.get("title", "")
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ [KB Manager] Vector database updated with new course")
        
        except Exception as e:
            logger.error(f"Error updating vector DB: {str(e)}")
    
    def _update_vector_db_assessment(self, assessment_data: Dict[str, Any]):
        """Update vector database with new assessment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO vector 
                (source_file, content_id, content_type, title, content, embedding_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "assessments.json",
                assessment_data.get("assessment_id", ""),
                "assessment",
                assessment_data.get("title", ""),
                json.dumps(assessment_data),
                assessment_data.get("title", "")
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ [KB Manager] Vector database updated with new assessment")
        
        except Exception as e:
            logger.error(f"Error updating vector DB: {str(e)}")
    
    def _update_vector_db_certification(self, cert_data: Dict[str, Any]):
        """Update vector database with new certification"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO vector 
                (source_file, content_id, content_type, title, content, embedding_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "certifications.json",
                cert_data.get("certification_id", ""),
                "certification",
                cert_data.get("title", ""),
                json.dumps(cert_data),
                cert_data.get("title", "")
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ [KB Manager] Vector database updated with new certification")
        
        except Exception as e:
            logger.error(f"Error updating vector DB: {str(e)}")
    
    def get_kb_status(self) -> Dict[str, Any]:
        """Get current knowledge base status"""
        try:
            status = {
                "total_courses": 0,
                "total_assessments": 0,
                "total_certifications": 0,
                "last_updated": "Never"
            }
            
            courses_file = self.kb_path / "course_structure.json"
            if courses_file.exists():
                with open(courses_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                status["total_courses"] = len(data.get("courses", []))
                status["last_updated"] = data.get("metadata", {}).get("last_updated", "Unknown")
            
            assessments_file = self.kb_path / "assessments.json"
            if assessments_file.exists():
                with open(assessments_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                status["total_assessments"] = len(data.get("assessments", []))
            
            certs_file = self.kb_path / "certifications.json"
            if certs_file.exists():
                with open(certs_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                status["total_certifications"] = len(data.get("certifications", []))
            
            return status
        
        except Exception as e:
            logger.error(f"Error getting KB status: {str(e)}")
            return {}


# Global KB Manager instance
_kb_manager_instance = None


def get_kb_manager(db_path: str) -> KBManager:
    """Get or create KB manager instance"""
    global _kb_manager_instance
    if _kb_manager_instance is None:
        _kb_manager_instance = KBManager(db_path)
    return _kb_manager_instance
