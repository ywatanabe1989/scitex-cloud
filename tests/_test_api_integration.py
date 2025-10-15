#!/usr/bin/env python3
"""
Test script for API key and impact factor integration
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append('/home/ywatanabe/proj/SciTeX-Cloud')
django.setup()

from apps.scholar_app.models import UserPreference
from django.contrib.auth.models import User

def test_api_key_functionality():
    """Test API key storage and retrieval"""
    print("🧪 Testing API Key functionality...")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Get user preferences
    prefs = UserPreference.get_or_create_for_user(user)
    
    # Test API key storage
    print("   Testing API key storage...")
    prefs.set_api_key('pubmed', 'test_api_key_12345')
    prefs.unpaywall_email = 'test@unpaywall.org'
    prefs.save()
    
    # Test API key retrieval
    print("   Testing API key retrieval...")
    retrieved_key = prefs.get_api_key('pubmed')
    print(f"   ✓ Retrieved API key: {retrieved_key}")
    
    # Test missing API keys detection
    print("   Testing missing API keys detection...")
    missing_keys = prefs.get_missing_api_keys()
    print(f"   ✓ Missing API keys: {missing_keys}")
    
    # Test API key existence check
    has_pubmed = prefs.has_api_key('pubmed')
    has_semantic = prefs.has_api_key('semantic_scholar')
    print(f"   ✓ Has PubMed key: {has_pubmed}")
    print(f"   ✓ Has Semantic Scholar key: {has_semantic}")
    
    print("✅ API Key functionality test completed!")
    return prefs

def test_impact_factor_integration():
    """Test impact factor search integration"""
    print("\n📊 Testing Impact Factor integration...")
    
    try:
        sys.path.insert(0, '/home/ywatanabe/proj/SciTeX-Cloud/externals/SciTeX-Scholar/src')
        from scitex_scholar.impact_factor_search import get_journal_impact_factor, JournalRankingSearch
        
        print("   Testing journal impact factor lookup...")
        
        # Test impact factor for well-known journals
        test_journals = [
            'Nature',
            'Science', 
            'Cell',
            'Journal of Neuroscience',
            'PLoS ONE'
        ]
        
        for journal in test_journals:
            try:
                impact_factor = get_journal_impact_factor(journal)
                print(f"   ✓ {journal}: IF = {impact_factor}")
            except Exception as e:
                print(f"   ⚠ {journal}: Error - {e}")
        
        # Test journal ranking search
        print("   Testing journal ranking search...")
        ranker = JournalRankingSearch()
        high_impact_journals = ranker.search_journals_by_impact_factor(
            min_impact_factor=10.0,
            limit=5
        )
        
        print(f"   ✓ Found {len(high_impact_journals)} high-impact journals:")
        for journal in high_impact_journals[:3]:
            print(f"      - {journal.get('name', 'Unknown')}: IF = {journal.get('impact_factor', 'N/A')}")
        
        print("✅ Impact Factor integration test completed!")
        
    except ImportError as e:
        print(f"   ⚠ Impact factor package not available: {e}")
    except Exception as e:
        print(f"   ❌ Impact factor test failed: {e}")

def test_search_integration():
    """Test the integrated search functionality"""
    print("\n🔍 Testing integrated search functionality...")
    
    try:
        from apps.scholar_app.simple_views import search_with_scitex_scholar
        
        # Test search with user preferences
        user = User.objects.get(username='test_user')
        prefs = UserPreference.get_or_create_for_user(user)
        
        print("   Testing search with user API keys...")
        results = search_with_scitex_scholar(
            query="machine learning",
            sources=['arxiv'],
            max_results=3,
            user_preferences=prefs
        )
        
        print(f"   ✓ Search returned {len(results)} results")
        for i, result in enumerate(results[:2], 1):
            title = result.get('title', 'Unknown')[:50]
            impact_factor = result.get('impact_factor', 'N/A')
            print(f"      {i}. {title}... (IF: {impact_factor})")
        
        print("✅ Search integration test completed!")
        
    except Exception as e:
        print(f"   ❌ Search integration test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Key and Impact Factor Integration Tests\n")
    
    # Test API key functionality
    prefs = test_api_key_functionality()
    
    # Test impact factor integration
    test_impact_factor_integration()
    
    # Test search integration
    test_search_integration()
    
    print("\n🎉 All tests completed!")