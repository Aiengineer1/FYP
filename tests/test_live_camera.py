#!/usr/bin/env python3
"""
Live Camera Feed Test Script
Tests real-time camera connectivity and displays live video feed
"""

import cv2
import time
from datetime import datetime

# Camera Configuration
ip_address = "192.168.0.5"  # Camera IP
username = "admin"          # Camera username
password = "admin1234"      # Camera password
rtsp_url = f"rtsp://{username}:{password}@{ip_address}:554/cam/realmonitor?channel=1&subtype=0"

class LiveCameraTester:
    def __init__(self, rtsp_url, camera_ip):
        self.rtsp_url = rtsp_url
        self.camera_ip = camera_ip
        self.cap = None
        self.frame_count = 0
        self.start_time = None
        
    def print_status(self, message, status="INFO"):
        """Print formatted status messages"""
        symbols = {"SUCCESS": "✅", "FAILED": "❌", "INFO": "ℹ️", "TESTING": "🔄"}
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {symbols.get(status, 'ℹ️')} {message}")
    
    def test_connectivity(self):
        """Test initial camera connectivity"""
        self.print_status(f"Testing connectivity to camera {self.camera_ip}...", "TESTING")
        self.print_status(f"RTSP URL: {self.rtsp_url}", "INFO")
        
        try:
            # Create VideoCapture object
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            # Set buffer size to reduce latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Set timeout
            self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)  # 10 seconds
            
            if not self.cap.isOpened():
                self.print_status(f"Failed to connect to camera {self.camera_ip}", "FAILED")
                return False
            
            # Try to read first frame
            ret, frame = self.cap.read()
            if ret and frame is not None:
                frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
                height, width = frame.shape[:2]
                self.print_status(f"Successfully connected to camera {self.camera_ip}", "SUCCESS")
                self.print_status(f"Frame resolution: {width}x{height}", "INFO")
                return True
            else:
                self.print_status(f"Connected but cannot read frames from {self.camera_ip}", "FAILED")
                return False
                
        except Exception as e:
            self.print_status(f"Connection error: {str(e)}", "FAILED")
            return False
    
    def display_live_feed(self):
        """Display live camera feed"""
        if not self.cap or not self.cap.isOpened():
            self.print_status("Camera not connected", "FAILED")
            return False
        
        self.print_status("Starting live video feed...", "SUCCESS")
        self.print_status("Press 'q' to quit, 's' to save frame, 'i' for info", "INFO")
        
        self.start_time = time.time()
        
        # Create window
        cv2.namedWindow('Live Camera Feed', cv2.WINDOW_NORMAL)
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    self.print_status("Failed to read frame, reconnecting...", "FAILED")
                    # Try to reconnect
                    self.cap.release()
                    time.sleep(1)
                    self.cap = cv2.VideoCapture(self.rtsp_url)
                    continue
                
                frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
                height, width = frame.shape[:2]
                
                self.frame_count += 1
                
                # Add overlay information
                self.add_frame_info(frame)
                
                # Display frame
                cv2.imshow('Live Camera Feed', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    self.print_status("Quitting live feed...", "INFO")
                    break
                elif key == ord('s'):
                    self.save_frame(frame)
                elif key == ord('i'):
                    self.show_stats()
                
                # Print periodic status
                if self.frame_count % 100 == 0:
                    self.show_stats()
                    
        except KeyboardInterrupt:
            self.print_status("Live feed interrupted by user", "INFO")
        except Exception as e:
            self.print_status(f"Live feed error: {str(e)}", "FAILED")
        finally:
            self.cleanup()
    
    def add_frame_info(self, frame):
        """Add information overlay to frame"""
        height, width = frame.shape[:2]
        
        # Calculate FPS
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        else:
            fps = 0
        
        # Add text overlay
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Background rectangles for text
        cv2.rectangle(frame, (10, 10), (400, 80), (0, 0, 0), -1)
        
        # Text information
        cv2.putText(frame, f"Camera: {self.camera_ip}", (15, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Time: {timestamp}", (15, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"FPS: {fps:.1f} | Frame: {self.frame_count}", (15, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def save_frame(self, frame):
        """Save current frame as image"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"camera_{self.camera_ip}_{timestamp}.jpg"
        
        try:
            cv2.imwrite(filename, frame)
            self.print_status(f"Frame saved as {filename}", "SUCCESS")
        except Exception as e:
            self.print_status(f"Failed to save frame: {str(e)}", "FAILED")
    
    def show_stats(self):
        """Show current statistics"""
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
            
            self.print_status(f"Stats - Frames: {self.frame_count}, "
                            f"Runtime: {elapsed_time:.1f}s, FPS: {fps:.1f}", "INFO")
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.print_status("Resources cleaned up", "INFO")

def main():
    """Main function"""
    print("🎥 Live Camera Feed Test")
    print("=" * 50)
    print(f"Camera IP: {ip_address}")
    print(f"Username: {username}")
    print(f"RTSP URL: {rtsp_url}")
    print("=" * 50)
    
    # Create tester instance
    tester = LiveCameraTester(rtsp_url, ip_address)
    
    # Test connectivity first
    if not tester.test_connectivity():
        print("\n❌ Cannot connect to camera. Please check:")
        print("   • Camera is powered on and connected to network")
        print("   • IP address is correct (192.168.0.5)")
        print("   • Username/password are correct (admin/admin1234)")
        print("   • Camera is accessible from this network")
        print("   • RTSP service is enabled on camera")
        return False
    
    # Start live feed
    print(f"\n🎬 Starting live feed from camera {ip_address}...")
    print("Controls:")
    print("   • Press 'q' to quit")
    print("   • Press 's' to save current frame")
    print("   • Press 'i' to show statistics")
    print("   • Ctrl+C to force quit")
    
    tester.display_live_feed()
    
    # Show final stats
    tester.show_stats()
    print("\n🎯 Live camera test completed!")
    
    return True

if __name__ == "__main__":
    main() 