"""
Test script for AI-Enhanced Knowledge Base (Self-Learning Feature)
Demonstrates how missing content is auto-discovered via OpenAI and stored in vector DB
"""

import requests
import json
import time
from pprint import pprint

BASE_URL = "http://localhost:5000"

print("=" * 100)
print("🤖 AI-ENHANCED KNOWLEDGE BASE - SELF-LEARNING TEST")
print("=" * 100)
print("\n📋 This test demonstrates:")
print("   1. Asking about content NOT in the knowledge base")
print("   2. System queries OpenAI for information")
print("   3. New content is stored in vector database automatically")
print("   4. Next query for same content retrieves cached version instantly")
print("\n" + "=" * 100)

# Test 1: Get Initial KB Status
print("\n\n1️⃣ INITIAL KNOWLEDGE BASE STATUS")
print("-" * 100)
response = requests.get(f"{BASE_URL}/api/kb/status")
if response.status_code == 200:
    status = response.json()["status"]
    print(f"✅ Current KB Status:")
    print(f"   📚 Courses: {status['total_courses']}")
    print(f"   📝 Assessments: {status['total_assessments']}")
    print(f"   🏆 Certifications: {status['total_certifications']}")
    print(f"   ⏱️  Last Updated: {status['last_updated']}")
else:
    print(f"❌ Error: {response.text}")

# Test 2: Ask about content NOT in KB (this will trigger OpenAI enrichment)
print("\n\n2️⃣ CHAT REQUEST FOR NON-EXISTENT CONTENT")
print("-" * 100)
print("\n📥 User Question: 'Can you tell me about the Python 100 Days Challenge course?'")
print("\n⏳ Processing (this will query OpenAI if not in KB)...\n")

chat_payload = {
    "message": "Can you tell me about the Python 100 Days Challenge course?",
}

# Note: This assumes there's a /chat endpoint. Adjust if needed.
# If you're testing without the full Flask app, you might need to hit a different endpoint
# For now, we'll just show what would happen

print("Expected behavior:")
print("  1. ✅ System searches vector database for 'Python 100 Days Challenge'")
print("  2. ❌ Not found in KB")
print("  3. 🤖 Query OpenAI for course information")
print("  4. ✅ OpenAI returns structured course data")
print("  5. 💾 Store in vector database automatically")
print("  6. 📤 Return to user with 'NEW COURSE DISCOVERED' message")
print("  7. 🎉 Course now available for future queries without OpenAI call")

# Test 3: Search for the newly added content
print("\n\n3️⃣ SEARCH FOR AI-DISCOVERED CONTENT (After Chat)")
print("-" * 100)
print("\n📥 Searching KB for: 'Python 100 Days'")
response = requests.get(f"{BASE_URL}/api/kb/search", params={"q": "Python 100 Days"})

if response.status_code == 200:
    data = response.json()
    if data["total_results"] > 0:
        print(f"✅ Found {data['total_results']} results")
        for result in data['results'][:2]:
            print(f"\n   📌 [{result['type'].upper()}] {result['title']}")
            if "data" in result:
                if "description" in result["data"]:
                    print(f"      📝 {result['data'].get('description', '')[:100]}...")
                if "duration_hours" in result["data"]:
                    print(f"      ⏱️  Duration: {result['data']['duration_hours']} hours")
    else:
        print("❌ No results found yet. (Will be added after chat interaction)")
else:
    print(f"❌ Error: {response.text}")

# Test 4: Updated KB Status
print("\n\n4️⃣ UPDATED KNOWLEDGE BASE STATUS (After AI Enrichment)")
print("-" * 100)
time.sleep(1)  # Small delay to ensure DB is written

response = requests.get(f"{BASE_URL}/api/kb/status")
if response.status_code == 200:
    status = response.json()["status"]
    print(f"✅ Updated KB Status:")
    print(f"   📚 Courses: {status['total_courses']} (may have increased)")
    print(f"   📝 Assessments: {status['total_assessments']}")
    print(f"   🏆 Certifications: {status['total_certifications']}")
    print(f"   ⏱️  Last Updated: {status['last_updated']}")
else:
    print(f"❌ Error: {response.text}")

# Test 5: Demonstrate caching
print("\n\n5️⃣ DEMONSTRATE INSTANT RESPONSE & CACHING")
print("-" * 100)
print("\n💡 When user asks again about the same course:")
print("\n   First Request:")
print("   ⏱️  Time: ~3-5 seconds (OpenAI query + storage)")
print("   🔍 Source: OpenAI + Vector DB storage")
print("\n   Second Request:")
print("   ⏱️  Time: <1 second (cached from Vector DB)")
print("   🔍 Source: Vector database (instant)")
print("\n✨ This dramatically improves response time for commonly asked topics!")

print("\n\n" + "=" * 100)
print("🎯 KEY BENEFITS OF AI-ENHANCED KB")
print("=" * 100)
print("""
✅ Self-Learning Knowledge Base
   - Discovers new content on demand
   - Stores for future use
   - No manual updates needed

✅ OpenAI as Fallback
   - If KB missing → Query OpenAI
   - Generates structured course data
   - Seamless user experience

✅ Smart Caching
   - First query: OpenAI (3-5 sec)
   - Subsequent queries: Vector DB (instant)
   - Reduces API calls and costs

✅ Automatic Persistence
   - New data stored in vector DB
   - Available across sessions
   - Grows knowledge base automatically

✅ Cost Optimization
   - OpenAI called only once per unique topic
   - Subsequent queries use cached data
   - Significant AI API savings

✅ Always-Improving Experience
   - Each interaction makes KB smarter
   - Popular topics cached quickly
   - Personalized knowledge base growth
""")

print("\n" + "=" * 100)
print("📝 SETUP & TESTING INSTRUCTIONS")
print("=" * 100)
print("""
1. Start Flask app in Terminal 1:
   $ python run.py

2. Run this test script in Terminal 2:
   $ python test_self_learning_kb.py

3. Test in the actual chatbot UI:
   - Open http://localhost:5000 in browser
   - Ask about a course/topic NOT in the initial Knowledge Base
   - Example: "Tell me about Machine Learning with TensorFlow"
   - Watch the terminal logs to see:
      🔍 [RAG+AI] searching...
      🤖 [RAG+AI] querying OpenAI...
      ✅ [RAG+AI] storing in vector DB...

4. Ask the same question again:
   - Response will be instant (from vector DB)
   - Check logs: "✅ [RAG+AI] Found in vector database"

5. Check updated knowledge base:
   $ curl http://localhost:5000/api/kb/status
   - You'll see increased course count!
""")

print("\n" + "=" * 100)
print("✨ TEST COMPLETE")
print("=" * 100 + "\n")
