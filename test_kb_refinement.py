"""
Test script for Knowledge Base Refinement System
Demonstrates adding new courses, assessments, and certifications
Run this after: python run.py (on another terminal)
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:5000"

print("=" * 80)
print("🚀 KNOWLEDGE BASE REFINEMENT SYSTEM - TEST SCRIPT")
print("=" * 80)

# Test 1: Get Current KB Status
print("\n1️⃣ Getting Knowledge Base Status...")
print("-" * 80)
response = requests.get(f"{BASE_URL}/api/kb/status")
if response.status_code == 200:
    print("✅ Current KB Status:")
    pprint(response.json()["status"])
else:
    print(f"❌ Error: {response.text}")

# Test 2: Add a New Course
print("\n\n2️⃣ Adding a New Course...")
print("-" * 80)
new_course = {
    "title": "Machine Learning with Scikit-learn",
    "description": "Learn machine learning fundamentals using Scikit-learn library. Cover supervised and unsupervised learning algorithms.",
    "duration_hours": 55,
    "level": "Intermediate",
    "instructor": "Dr. Michael Chen",
    "modules": [
        {
            "module_id": "ML001",
            "title": "ML Fundamentals",
            "lessons": []
        },
        {
            "module_id": "ML002",
            "title": "Supervised Learning",
            "lessons": []
        }
    ]
}

print(f"Adding course: {new_course['title']}")
response = requests.post(f"{BASE_URL}/api/kb/add-course", json=new_course)
if response.status_code == 201:
    print("✅ Course added successfully!")
    pprint(response.json())
else:
    print(f"❌ Error: {response.text}")

# Test 3: Add Another Course
print("\n\n3️⃣ Adding Another Course...")
print("-" * 80)
new_course_2 = {
    "title": "Docker and Kubernetes Mastery",
    "description": "Master containerization with Docker and orchestration with Kubernetes. Learn deployment best practices.",
    "duration_hours": 60,
    "level": "Advanced",
    "instructor": "David Docker",
}

print(f"Adding course: {new_course_2['title']}")
response = requests.post(f"{BASE_URL}/api/kb/add-course", json=new_course_2)
if response.status_code == 201:
    print("✅ Course added successfully!")
    pprint(response.json())
else:
    print(f"❌ Error: {response.text}")

# Test 4: Add a New Assessment
print("\n\n4️⃣ Adding a New Assessment...")
print("-" * 80)
new_assessment = {
    "title": "Machine Learning Hands-on Project",
    "description": "Build a complete machine learning pipeline with data preprocessing, model training, and evaluation.",
    "type": "project",
    "difficulty": "Hard",
    "questions": [
        {
            "question_id": "Q1",
            "text": "Implement a random forest classifier",
            "points": 25
        },
        {
            "question_id": "Q2",
            "text": "Perform hyperparameter tuning using GridSearchCV",
            "points": 25
        }
    ],
    "duration_minutes": 240
}

print(f"Adding assessment: {new_assessment['title']}")
response = requests.post(f"{BASE_URL}/api/kb/add-assessment", json=new_assessment)
if response.status_code == 201:
    print("✅ Assessment added successfully!")
    pprint(response.json())
else:
    print(f"❌ Error: {response.text}")

# Test 5: Add a Certification
print("\n\n5️⃣ Adding a New Certification...")
print("-" * 80)
new_cert = {
    "title": "AWS Certified Solutions Architect",
    "description": "Design and implement scalable cloud solutions on AWS. Learn best practices for building reliable, efficient, and secure applications.",
    "duration_weeks": 16,
    "skills_covered": [
        "EC2 & Auto Scaling",
        "RDS Database Design",
        "S3 & CloudFront",
        "VPC & Networking",
        "IAM & Security",
        "CloudWatch Monitoring"
    ],
    "requirements": {
        "prerequisites": "Basic cloud knowledge or AWS Fundamentals certification",
        "exam_fee": 150,
        "passing_score": 720,
        "exam_duration_minutes": 130
    },
    "issuing_body": "Amazon Web Services"
}

print(f"Adding certification: {new_cert['title']}")
response = requests.post(f"{BASE_URL}/api/kb/add-certification", json=new_cert)
if response.status_code == 201:
    print("✅ Certification added successfully!")
    pprint(response.json())
else:
    print(f"❌ Error: {response.text}")

# Test 6: Search Knowledge Base
print("\n\n6️⃣ Searching Knowledge Base...")
print("-" * 80)
search_queries = ["Machine Learning", "Docker", "Python"]

for query in search_queries:
    print(f"\nSearching for: '{query}'")
    response = requests.get(f"{BASE_URL}/api/kb/search", params={"q": query})
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Found {data['total_results']} results")
        for result in data['results']:
            print(f"      - [{result['type'].upper()}] {result['title']}")
    else:
        print(f"   ❌ Error: {response.text}")

# Test 7: Check Updated KB Status
print("\n\n7️⃣ Getting Updated Knowledge Base Status...")
print("-" * 80)
response = requests.get(f"{BASE_URL}/api/kb/status")
if response.status_code == 200:
    print("✅ Updated KB Status:")
    pprint(response.json()["status"])
else:
    print(f"❌ Error: {response.text}")

# Test 8: Test Duplicate Prevention
print("\n\n8️⃣ Testing Duplicate Prevention...")
print("-" * 80)
duplicate_course = {
    "title": "Machine Learning with Scikit-learn",  # Same as course added earlier
    "description": "Attempt to add duplicate course",
    "duration_hours": 50,
    "level": "Beginner",
    "instructor": "Someone Else"
}

print("Attempting to add duplicate course...")
response = requests.post(f"{BASE_URL}/api/kb/add-course", json=duplicate_course)
if response.status_code == 400:
    print("✅ Duplicate correctly prevented!")
    pprint(response.json())
else:
    print(f"⚠️  Unexpected response: {response.status_code}")

print("\n" + "=" * 80)
print("✨ TEST SCRIPT COMPLETE")
print("=" * 80)
print("\n📝 Next Steps:")
print("   1. Check the Knowledge base/ folder - files are updated with new content")
print("   2. Ask the chatbot about the new courses you added")
print("   3. Verify RAG augmentation in the chat responses")
print("   4. Check app logs for '[KB Manager]' and '[RAG]' debug messages")
print("\n")
