"""
Example usage and testing for AquilaTrace API.
Run this file to test all endpoints.
"""
import requests
import json
from typing import Dict, Any
import time

BASE_URL = "http://localhost:10000"


def print_response(title: str, response: requests.Response) -> Dict[str, Any]:
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except:
        print(response.text)
        return {}


def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print_response("HEALTH CHECK", response)
    assert response.status_code == 200


def test_full_analysis():
    """Test full analysis endpoint."""
    payload = {
        "file_path": None  # Uses default from config
    }
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    result = print_response("FULL ANALYSIS", response)
    assert response.status_code == 200
    return result


def test_quick_analysis():
    """Test quick analysis endpoint."""
    response = requests.get(f"{BASE_URL}/analyze/quick", params={"threshold": 0.5})
    print_response("QUICK ANALYSIS", response)
    assert response.status_code == 200


def test_with_custom_file():
    """Test analysis with custom file path."""
    payload = {
        "file_path": "data/transactions.csv"
    }
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    print_response("ANALYSIS WITH CUSTOM FILE", response)
    

def run_all_tests():
    """Run all API tests."""
    print("\n" + "="*60)
    print("  AquilaTrace API Test Suite")
    print("="*60)
    print("\nMake sure the server is running: python main.py")
    
    try:
        # Test health check
        print("\n[1/4] Testing Health Check...")
        test_health_check()
        print("✓ Health check passed")
        
        # Test full analysis
        print("\n[2/4] Testing Full Analysis...")
        result = test_full_analysis()
        if result:
            print(f"✓ Analysis complete: {result.get('total_transactions', 0)} transactions analyzed")
        
        # Test quick analysis
        print("\n[3/4] Testing Quick Analysis...")
        test_quick_analysis()
        print("✓ Quick analysis passed")
        
        # Test with custom file
        print("\n[4/4] Testing Custom File Path...")
        test_with_custom_file()
        print("✓ Custom file analysis passed")
        
        print("\n" + "="*60)
        print("  All Tests Passed! ✓")
        print("="*60)
        print("\nAPI is ready for use!")
        print(f"  Dashboard: {BASE_URL}/dashboard")
        print(f"  API Docs: {BASE_URL}/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print(f"Make sure the server is running on {BASE_URL}")
        print("Run: python main.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    run_all_tests()
