#!/usr/bin/env python3
"""
Start Backend Server for Testing
Runs the FastAPI server with Socket.io support
"""

import subprocess
import sys
import time
import requests
from datetime import datetime

def check_server_health(max_attempts=10):
    """Check if server is running and healthy"""
    print("🔍 Checking server health...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ Server is healthy and responding!")
                health_data = response.json()
                print(f"   Message: {health_data.get('message', 'N/A')}")
                print(f"   Version: {health_data.get('version', 'N/A')}")
                return True
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts}: Server not ready yet...")
            time.sleep(2)
    
    print("❌ Server health check failed after maximum attempts")
    return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 STARTING BACKEND SERVER")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    try:
        # Start the server using run.py
        print("📡 Starting server with Socket.io support...")
        print("🌐 Server will be available at: http://localhost:8000")
        print("🔌 Socket.io endpoint: http://localhost:8000/socket.io/")
        print("📚 API Docs: http://localhost:8000/docs")
        print("-" * 60)
        print("📊 Server logs:")
        print("-" * 60)
        
        # Run the server
        subprocess.run([sys.executable, "run.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user (Ctrl+C)")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Just check if server is running
        check_server_health()
    else:
        # Start the server
        start_server() 