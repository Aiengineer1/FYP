#!/usr/bin/env python3
"""
Master Test Runner
Runs all backend test suites and provides comprehensive results
"""

import subprocess
import sys
import time
import requests
from datetime import datetime

def check_server_running():
    """Check if the backend server is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_test_suite(test_file, test_name):
    """Run a specific test suite"""
    print("="*80)
    print("RUNNING " + test_name.upper())
    print("="*80)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running {test_name}: {str(e)}")
        return False

def main():
    """Main test runner"""
    print("BACKEND COMPREHENSIVE TEST SUITE")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Backend server is not running!")
        print("🚀 Please start the server first:")
        print("   python start_server.py")
        print("\n   OR in a separate terminal:")
        print("   python run.py")
        print("\n   Then run this test suite again.")
        return False
    
    print("✅ Backend server is running and healthy!")
    
    # Define test suites
    test_suites = [
        ("test_complete_backend.py", "Complete Backend Integration Tests"),
        ("test_camera_worker.py", "Camera Worker & Detection Pipeline Tests"),
        ("test_socketio.py", "Socket.io WebSocket Tests"),
    ]
    
    results = {}
    
    # Run each test suite
    for test_file, test_name in test_suites:
        print(f"\n⏳ Starting {test_name}...")
        time.sleep(1)  # Brief pause between tests
        
        success = run_test_suite(test_file, test_name)
        results[test_name] = success
        
        if success:
            print(f"✅ {test_name} - COMPLETED SUCCESSFULLY")
        else:
            print(f"❌ {test_name} - FAILED")
        
        time.sleep(2)  # Pause between test suites
    
    # Final Results Summary
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST RESULTS SUMMARY")
    print(f"{'='*80}")
    
    total_suites = len(results)
    passed_suites = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Test Suites Passed: {passed_suites}/{total_suites}")
    print(f"   Success Rate: {(passed_suites/total_suites)*100:.1f}%")
    
    if passed_suites == total_suites:
        print("\n🎉 ALL TEST SUITES PASSED!")
        print("🚀 Backend is fully functional and ready for production!")
        print("\n📋 Verified Features:")
        print("   ✅ Authentication (JWT, signup, login)")
        print("   ✅ Database operations (Mall, Camera, Customer)")
        print("   ✅ Analytics engine & real-time calculations")
        print("   ✅ Socket.io WebSocket connectivity")
        print("   ✅ Camera processing pipeline")
        print("   ✅ API endpoints & error handling")
    else:
        print(f"\n⚠️  {total_suites - passed_suites} test suite(s) failed")
        print("🔍 Review the detailed output above for specific issues")
    
    print(f"\n⏰ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed_suites == total_suites

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 