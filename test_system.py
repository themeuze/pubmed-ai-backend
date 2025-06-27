#!/usr/bin/env python3
"""
Test script voor PubMed RAG System
Test alle componenten van het systeem
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_search():
    """Test search functionality"""
    print("\n🔍 Testing search functionality...")
    try:
        search_data = {
            "query": "omega-3 fatty acids",
            "max_results": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Search successful: {result.get('articles_processed', 0)} articles processed")
                return True
            else:
                print(f"❌ Search failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Search request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def test_ask():
    """Test question asking functionality"""
    print("\n💬 Testing question asking...")
    try:
        question_data = {
            "question": "Wat zijn de gezondheidsvoordelen van omega-3 vetzuren?",
            "n_results": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/ask",
            json=question_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Question answered successfully")
                print(f"   Response: {result.get('response', '')[:100]}...")
                print(f"   Context sources: {result.get('context_count', 0)}")
                return True
            else:
                print(f"❌ Question failed: {result.get('response', 'Unknown error')}")
                return False
        else:
            print(f"❌ Question request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Question error: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats retrieved successfully")
            print(f"   Total chunks: {stats.get('vector_store', {}).get('total_chunks', 0)}")
            print(f"   Embedder model: {stats.get('embedder_model', 'N/A')}")
            print(f"   Chat model: {stats.get('chat_model', 'N/A')}")
            return True
        else:
            print(f"❌ Stats request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return False

def test_examples():
    """Test examples endpoint"""
    print("\n📝 Testing examples endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/examples")
        if response.status_code == 200:
            examples = response.json()
            print("✅ Examples retrieved successfully")
            print(f"   Search examples: {len(examples.get('search_examples', []))}")
            print(f"   Question examples: {len(examples.get('question_examples', []))}")
            return True
        else:
            print(f"❌ Examples request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Examples error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting PubMed RAG System Tests")
    print("=" * 50)
    
    # Wait for system to be ready
    print("⏳ Waiting for system to be ready...")
    time.sleep(10)
    
    tests = [
        test_health,
        test_search,
        test_ask,
        test_stats,
        test_examples
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs for more details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 