#!/usr/bin/env python3
"""
RTSP URL Testing Script
Test the specific RTSP URLs for the user's 4 cameras to verify connectivity.
"""

import cv2
import time

def test_rtsp_url(ip_address, username="admin", password="admin1234"):
    """Test a specific RTSP URL"""
    
    # Standard RTSP URL format used in your app
    rtsp_url = f"rtsp://{username}:{password}@{ip_address}:554/cam/realmonitor?channel=1&subtype=0"
    
    print(f"Testing: {rtsp_url}")
    
    try:
        # Try to connect to RTSP stream
        cap = cv2.VideoCapture(rtsp_url)
        
        if not cap.isOpened():
            print(f"Failed to connect to {ip_address}")
            return False
        
        # Try to read a frame
        ret, frame = cap.read()
        
        if ret and frame is not None:
            height, width = frame.shape[:2]
            print(f"Success! Camera {ip_address} - Frame size: {width}x{height}")
            cap.release()
            return True
        else:
            print(f"Connected but no frame from {ip_address}")
            cap.release()
            return False
            
    except Exception as e:
        print(f"Error testing {ip_address}: {str(e)}")
        return False

def test_alternative_rtsp_paths(ip_address, username="admin", password="admin1234"):
    """Test alternative RTSP paths that might work"""
    
    alternative_paths = [
        "/cam/realmonitor?channel=1&subtype=0",  # Current path
        "/stream1",                              # Common path
        "/stream",                               # Simple path
        "/cam/realmonitor?channel=1&subtype=1",  # Different subtype
        "/live",                                 # Another common path
        "/h264",                                 # H264 stream
        "/mjpeg",                               # MJPEG stream
    ]
    
    print(f"\nTesting alternative RTSP paths for {ip_address}:")
    
    for path in alternative_paths:
        rtsp_url = f"rtsp://{username}:{password}@{ip_address}:554{path}"
        print(f"   Testing: {path}")
        
        try:
            cap = cv2.VideoCapture(rtsp_url)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"   ✅ SUCCESS with {path} - Frame: {width}x{height}")
                    cap.release()
                    return path
                cap.release()
        except:
            pass
    
    print(f"   ❌ No alternative paths worked for {ip_address}")
    return None

def main():
    print("RTSP URL Testing for Your 4 Cameras")
    print("=" * 50)
    print("Camera IPs: 192.68.0.2, 192.68.0.3, 192.68.0.4, 192.68.0.5")
    print("Username: admin, Password: admin1234")
    print("=" * 50)
    
    # Your camera IP addresses
    camera_ips = ["192.68.0.2", "192.68.0.3", "192.68.0.4", "192.68.0.5"]
    
    successful_cameras = []
    failed_cameras = []
    
    for i, ip in enumerate(camera_ips, 1):
        print(f"\n--- Camera {i} ({ip}) ---")
        
        # Test standard RTSP URL
        if test_rtsp_url(ip):
            successful_cameras.append(ip)
        else:
            failed_cameras.append(ip)
            # Try alternative paths
            working_path = test_alternative_rtsp_paths(ip)
            if working_path:
                successful_cameras.append(ip)
                failed_cameras.remove(ip)
        
        time.sleep(1)  # Small delay between tests
    
    print(f"\n{'=' * 50}")
    print("RTSP Testing Results:")
    print(f"✅ Working cameras: {len(successful_cameras)}/{len(camera_ips)}")
    print(f"❌ Failed cameras: {len(failed_cameras)}/{len(camera_ips)}")
    
    if successful_cameras:
        print(f"\n✅ Successfully connected to:")
        for ip in successful_cameras:
            rtsp_url = f"rtsp://admin:admin1234@{ip}:554/cam/realmonitor?channel=1&subtype=0"
            print(f"   📹 {ip}: {rtsp_url}")
    
    if failed_cameras:
        print(f"\n❌ Failed to connect to:")
        for ip in failed_cameras:
            print(f"   📹 {ip}")
        
        print("\n💡 Troubleshooting tips:")
        print("   • Check if cameras are powered on and network connected")
        print("   • Verify IP addresses are correct")
        print("   • Confirm username/password (admin/admin1234)")
        print("   • Check if cameras are on the same network")
        print("   • Try accessing camera web interface first")
    
    print(f"\n📋 Your App's RTSP URL Format:")
    print(f"rtsp://admin:admin1234@{{camera_ip}}:554/cam/realmonitor?channel=1&subtype=0")

if __name__ == "__main__":
    main() 