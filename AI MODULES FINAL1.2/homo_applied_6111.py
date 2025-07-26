import cv2
import numpy as np
import json
import os

# --- Camera RTSP variables (replace with your actual RTSP URLs) ---
CAMERA_RTSP = {
    'cam1': 'rtsp://admin:admin1234@192.168.0.2:554/cam/realmonitor?channel=1&subtype=0',
    'cam2': 'rtsp://admin:admin1234@192.168.0.3:554/cam/realmonitor?channel=1&subtype=0',
    'cam3': 'rtsp://admin:admin1234@192.168.0.4:554/cam/realmonitor?channel=1&subtype=0',
    'cam4': 'rtsp://admin:admin1234@192.168.0.5:554/cam/realmonitor?channel=1&subtype=0',
    # Add more cameras as needed
}
CAMERA_NUM_TO_NAME = {'1': 'cam1', '2': 'cam2', '3': 'cam3', '4': 'cam4'}

# --- Camera selection (frontend-driven) ---
print("Available cameras:")
for num, cam in CAMERA_NUM_TO_NAME.items():
    print(f"  {num}: {cam} -> {CAMERA_RTSP[cam]}")
camera_input = input("Enter camera number or name for this mapping (1, 2, 3, 4, cam1, cam2, etc.): ").strip()

# Map numeric input to camera name
camera_name = CAMERA_NUM_TO_NAME.get(camera_input, camera_input)

if camera_name not in CAMERA_RTSP:
    raise ValueError(f"Camera '{camera_input}' not found in CAMERA_RTSP. Please add it to the dictionary.")

# --- Lab map selection (frontend-driven) ---
lab_map_path = None
if os.path.exists('selected_lab_map.txt'):
    with open('selected_lab_map.txt', 'r') as f:
        lab_map_path = f.read().strip()
if not lab_map_path or not os.path.exists(lab_map_path):
    raise FileNotFoundError("Lab map image path not found. Please run main.py and select a floorplan image first.")

# --- Capture a real-time frame from the selected camera's RTSP stream ---
rtsp_url = CAMERA_RTSP[camera_name]
cap = cv2.VideoCapture(rtsp_url)
ret, camera_frame = cap.read()
cap.release()
if not ret or camera_frame is None:
    raise RuntimeError(f"Failed to capture frame from RTSP stream: {rtsp_url}")

# --- Load lab map image ---
lab_map = cv2.imread(lab_map_path)
if lab_map is None:
    raise RuntimeError(f"Failed to load lab map image: {lab_map_path}")

# Resize both images to same dimensions
target_size = (1280, 720)
camera_resized = cv2.resize(camera_frame, target_size, interpolation=cv2.INTER_AREA)

# Lists to store multiple objects
objects = []  # Stores dicts of (src_points, dst_points, name)
current_src = []
current_dst = []
selection_mode = "camera"

# --- New: Track if global zone is selected ---
global_zone_selected = False

def draw_points(image, points):
    for i, (x, y) in enumerate(points):
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        cv2.putText(image, str(i + 1), (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

def select_points(event, x, y, flags, param):
    global current_src, current_dst, selection_mode, camera_resized, lab_map
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if selection_mode == "camera" and len(current_src) < 4:
            current_src.append((x, y))
            draw_points(camera_resized, current_src)
            cv2.imshow("Select 4 points on Camera Frame", camera_resized)

        elif selection_mode == "map" and len(current_dst) < 4:
            current_dst.append((x, y))
            draw_points(lab_map, current_dst)
            cv2.imshow("Select 4 corresponding points on Lab Map", lab_map)
        
        if len(current_src) == 4 and len(current_dst) == 4:
            object_name = param.get('object_name', None)
            if object_name is None:
                object_name = input("Enter object name: ")
            objects.append({
                "name": object_name,
                "src_points": current_src.copy(),
                "dst_points": current_dst.copy()
            })
            print(f"Object '{object_name}' added.")
            current_src.clear()
            current_dst.clear()
            selection_mode = "camera"

# --- Step 1: Select global zone ---
print("\nSelect points for the GLOBAL ZONE on Camera Frame (minimum 4, can add more)")
camera_resized = cv2.resize(camera_frame, target_size, interpolation=cv2.INTER_AREA)
global_zone_src = []
cv2.imshow("Select points on Camera Frame (Global Zone)", camera_resized)

def global_zone_select_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global_zone_src.append((x, y))
        draw_points(camera_resized, global_zone_src)
        cv2.imshow("Select points on Camera Frame (Global Zone)", camera_resized)

cv2.setMouseCallback("Select points on Camera Frame (Global Zone)", global_zone_select_points)

while True:
    key = cv2.waitKey(0)
    if len(global_zone_src) >= 4:
        more = input("Do you want to add another point to the global zone? (y/n): ")
        if more.lower() != 'y':
            break
    else:
        print(f"Selected {len(global_zone_src)} points. Please select at least 4.")
cv2.destroyAllWindows()

print("\nSelect corresponding points for the GLOBAL ZONE on Lab Map (same number as before)")
global_zone_dst = []
lab_map_display = lab_map.copy()
cv2.imshow("Select points on Lab Map (Global Zone)", lab_map_display)

def global_zone_select_points_dst(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global_zone_dst.append((x, y))
        draw_points(lab_map_display, global_zone_dst)
        cv2.imshow("Select points on Lab Map (Global Zone)", lab_map_display)

cv2.setMouseCallback("Select points on Lab Map (Global Zone)", global_zone_select_points_dst)

while len(global_zone_dst) < len(global_zone_src):
    key = cv2.waitKey(0)
    if len(global_zone_dst) < len(global_zone_src):
        print(f"Selected {len(global_zone_dst)} points. Please select {len(global_zone_src) - len(global_zone_dst)} more.")
cv2.destroyAllWindows()

objects.append({
    "name": "global_zone",
    "src_points": global_zone_src,
    "dst_points": global_zone_dst
})
print("Global zone mapping saved. Now map regular objects as before.")

# --- Step 2: Map regular objects as before ---
while True:
    # Reset images for each new object
    camera_resized = cv2.resize(camera_frame, target_size, interpolation=cv2.INTER_AREA)
    lab_map_display = lab_map.copy()

    print("\nSelect 4 points on Camera Frame")
    cv2.imshow("Select 4 points on Camera Frame", camera_resized)
    cv2.setMouseCallback("Select 4 points on Camera Frame", select_points, param={})
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\nSelect 4 corresponding points on Lab Map")
    selection_mode = "map"
    cv2.imshow("Select 4 corresponding points on Lab Map", lab_map_display)
    cv2.setMouseCallback("Select 4 corresponding points on Lab Map", select_points, param={})
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    more = input("Do you want to add another object? (y/n): ")
    if more.lower() != 'y':
        break

# Save mappings to JSON
with open(f"homography_mappings_{camera_name}.json", "w") as f:
    json.dump(objects, f, indent=4)

print(f"Homography mappings (including global zone) saved successfully as homography_mappings_{camera_name}.json.")
