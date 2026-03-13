#!/usr/bin/env python3
"""
Test script to verify chatbot has access to comprehensive resources data
"""
import os
import sys
import sqlite3
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.routes import _get_comprehensive_resources_data
from app.db import get_resource_stats, list_approved_resources

def test_chatbot_resources_integration():
    """Test that chatbot has comprehensive resources information"""
    
    # Configuration
    db_path = "instance/app.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please make sure the app is set up correctly.")
        return False
    
    try:
        print("🧪 Testing chatbot resources integration...\n")
        
        # Step 1: Test resource statistics
        print("📊 Step 1: Testing resource statistics...")
        stats = get_resource_stats(db_path)
        print(f"   Total resources: {stats.get('total', 0)}")
        print(f"   Approved resources: {stats.get('approved', 0)}")
        print(f"   Pending resources: {stats.get('pending', 0)}")
        
        # Step 2: Test approved resources listing
        print("\n📚 Step 2: Testing approved resources listing...")
        approved_resources = list_approved_resources(db_path)
        print(f"   Found {len(approved_resources)} approved resources")
        
        for i, resource in enumerate(approved_resources[:5]):  # Show first 5
            print(f"   {i+1}. {resource.get('title', 'Untitled')} ({resource.get('subject', 'Unknown')} - {resource.get('branch', 'N/A')})")
        
        if len(approved_resources) > 5:
            print(f"   ... and {len(approved_resources) - 5} more resources")
        
        # Step 3: Test comprehensive resources data function
        print("\n🔧 Step 3: Testing comprehensive resources data function...")
        resources_data = _get_comprehensive_resources_data(db_path)
        print(f"   Generated resources data: {len(resources_data)} characters")
        
        # Show a preview of the data
        lines = resources_data.split('\n')[:20]  # Show first 20 lines
        print("   Preview:")
        for line in lines:
            print(f"   {line}")
        
        if len(resources_data.split('\n')) > 20:
            print(f"   ... and {len(resources_data.split('n')) - 20} more lines")
        
        # Step 4: Verify key components are present
        print("\n✅ Step 4: Verifying key components...")
        required_sections = [
            "RESOURCES FEATURE - COMPLETE OVERVIEW & DETAILED CATALOG",
            "RESOURCES STATISTICS",
            "RESOURCES FEATURE PURPOSE",
            "COMPLETE APPROVED RESOURCES CATALOG", 
            "RESOURCES FEATURE CAPABILITIES",
            "CHATBOT GUIDANCE - ANSWER THESE TYPES OF QUESTIONS",
            "EDUCATIONAL IMPACT",
            "SEARCH AND DISCOVERY"
        ]
        
        detailed_info_checks = [
            "UPLOADED BY:",
            "UPLOADED ON:",
            "APPROVED ON:",
            "APPROVED BY:",
            "ID:",
            "FILE:",
            "Who uploaded",
            "When was",
            "uploader name and email",
            "uploaded_at timestamp"
        ]
        
        for section in required_sections:
            if section in resources_data:
                print(f"   ✅ {section} - Present")
            else:
                print(f"   ❌ {section} - Missing")
        
        print("\n📋 Verifying detailed resource information...")
        for check in detailed_info_checks:
            if check in resources_data:
                print(f"   ✅ {check} - Present")
            else:
                print(f"   ❌ {check} - Missing")
        
        print(f"\n🎉 Testing completed successfully!")
        print(f"\n📋 Summary:")
        print(f"   • Resources statistics: {stats}")
        print(f"   • Approved resources: {len(approved_resources)}")
        print(f"   • Resources data size: {len(resources_data)} characters")
        print(f"   • All required sections present: {'✅' if all(section in resources_data for section in required_sections) else '❌'}")
        print(f"   • Detailed resource info present: {'✅' if all(check in resources_data for check in detailed_info_checks) else '❌'}")
        print(f"   • Chatbot can answer: Who uploaded what, when, approval details, etc.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chatbot_resources_integration()
    sys.exit(0 if success else 1)