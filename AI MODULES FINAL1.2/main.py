import os
from registry import GlobalPersonRegistry
from camera_tracker import CameraTracker
from zone_utils import load_global_zone_from_json, compute_polygon_overlap
import threading
import time
import cv2
import numpy as np
import json
import matplotlib.pyplot as plt


# --- Camera configs (copied from detect_track_and_map_person_age_gender_v3.py) ---
CAMERA_MAPPINGS = {
    'cam1': 'homography_mappings_cam1.json',
    'cam2': 'homography_mappings_cam2.json',
    'cam3': 'homography_mappings_cam3.json',
    'cam4': 'homography_mappings_cam4.json',
    # Add more cameras as needed
}
CAMERA_RTSP = {
    'cam1': 'rtsp://admin:admin1234@192.168.0.2:554/cam/realmonitor?channel=1&subtype=0',
    'cam2': 'rtsp://admin:admin1234@192.168.0.3:554/cam/realmonitor?channel=1&subtype=0',
    'cam3': 'rtsp://admin:admin1234@192.168.0.4:554/cam/realmonitor?channel=1&subtype=0',
    'cam4': 'rtsp://admin:admin1234@192.168.0.5:554/cam/realmonitor?channel=1&subtype=0',
    # Add more cameras as needed
}
CAMERA_OFFSETS = {
    'cam1': {'x_offset': 250, 'y_offset': -120},
    'cam2': {'x_offset': 0, 'y_offset': -200},
    'cam3': {'x_offset': 0, 'y_offset': 0},
    'cam4': {'x_offset': -50, 'y_offset': 150},
    # Add more cameras as needed
}
CAMERA_NUM_TO_NAME = {'1': 'cam1', '2': 'cam2', '3': 'cam3', '4': 'cam4'}

MALL_MAP_IMG = 'floorplan_gui.png'

# Prompt user for floorplan image path at the start
floorplan_path = input("Enter path to floorplan/mall map image (e.g., floorplan_gui.png): ").strip()
if not os.path.exists(floorplan_path):
    print(f"[ERROR] Floorplan image not found at {floorplan_path}")
    exit(1)
# Save the selected path for use by other modules
with open('selected_lab_map.txt', 'w') as f:
    f.write(floorplan_path)

def prompt_mode():
    print("\nSelect mode:")
    print("1. Single Camera Mode (prompt user)")
    print("2. Multi-Camera Mode (all available cameras)")
    mode = input("Enter 1 or 2: ").strip()
    return mode

def prompt_camera():
    print("Available cameras:")
    for num, cam in CAMERA_MAPPINGS.items():
        print(f"  {num}: {cam}")
    cam_input = input("Enter camera name or number (e.g., 1, cam1, ...): ").strip()
    # Map number to name if needed
    cam_name = CAMERA_NUM_TO_NAME.get(cam_input, cam_input)
    return cam_name

def generate_heatmap_from_routes(json_path, mall_map_path, output_path):
    # Load mall map image
    mall_map = cv2.imread(mall_map_path)
    if mall_map is None:
        print(f"Mall map image not found at {mall_map_path}")
        return
    height, width = mall_map.shape[:2]
    # Initialize heatmap matrix
    heatmap = np.zeros((height, width), dtype=np.float32)
    # Load person routes
    with open(json_path, 'r') as f:
        routes_data = json.load(f)
    # Accumulate heat for each route point
    for person in routes_data.values():
        for x, y in person.get('route', []):
            if 0 <= int(y) < height and 0 <= int(x) < width:
                heatmap[int(y), int(x)] += 1
    # Smooth heatmap
    heatmap_blur = cv2.GaussianBlur(heatmap, (0, 0), sigmaX=25, sigmaY=25)
    # Normalize to 0-255
    norm_heatmap = cv2.normalize(heatmap_blur, None, 0, 255, cv2.NORM_MINMAX)
    norm_heatmap = norm_heatmap.astype(np.uint8)
    # Apply colormap
    color_heatmap = cv2.applyColorMap(norm_heatmap, cv2.COLORMAP_JET)
    # Overlay heatmap on mall map
    overlay = cv2.addWeighted(mall_map, 0.6, color_heatmap, 0.4, 0)
    # Save result
    cv2.imwrite(output_path, overlay)
    print(f"Heatmap overlay saved to {output_path}")

def generate_person_object_interaction_bar(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    person_ids = []
    object_names = set()
    interaction_matrix = {}
    for pid, pdata in data.items():
        person_ids.append(pid)
        for obj, info in pdata.get('interactions', {}).items():
            object_names.add(obj)
            interaction_matrix.setdefault(pid, {})[obj] = info.get('duration_sec', 0)
    object_names = sorted(object_names)
    # Build matrix for plotting
    values = []
    for pid in person_ids:
        row = [interaction_matrix.get(pid, {}).get(obj, 0) for obj in object_names]
        values.append(row)
    # Plot
    x = np.arange(len(object_names))
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.8 / max(1, len(person_ids))
    for i, (pid, row) in enumerate(zip(person_ids, values)):
        ax.bar(x + i * bar_width, row, width=bar_width, label=pid)
    ax.set_xticks(x + bar_width * (len(person_ids) - 1) / 2)
    ax.set_xticklabels(object_names, rotation=30, ha='right')
    ax.set_ylabel('Interaction Time (sec)')
    ax.set_title('Interaction Time per Person per Object')
    ax.legend(title='Person ID')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Bar graph saved to {output_path}")


def generate_age_object_interaction_bar(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    age_object_duration = {}
    object_names = set()
    for pdata in data.values():
        age = str(pdata.get('age', 'Unknown') or 'Unknown')
        for obj, info in pdata.get('interactions', {}).items():
            object_names.add(obj)
            age_object_duration.setdefault(age, {}).setdefault(obj, 0)
            age_object_duration[age][obj] += info.get('duration_sec', 0)
    object_names = sorted(object_names)
    ages = sorted(age_object_duration.keys())
    # Build matrix for plotting
    values = []
    for age in ages:
        row = [age_object_duration[age].get(obj, 0) for obj in object_names]
        values.append(row)
    # Plot
    x = np.arange(len(object_names))
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.8 / max(1, len(ages))
    for i, (age, row) in enumerate(zip(ages, values)):
        ax.bar(x + i * bar_width, row, width=bar_width, label=age)
    ax.set_xticks(x + bar_width * (len(ages) - 1) / 2)
    ax.set_xticklabels(object_names, rotation=30, ha='right')
    ax.set_ylabel('Total Interaction Time (sec)')
    ax.set_title('Interaction Time per Object Grouped by Age')
    ax.legend(title='Age Group')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Bar graph saved to {output_path}")

def main():
    mode = prompt_mode()
    registry = GlobalPersonRegistry(similarity_threshold=0.75, history_size=5)
    trackers = []
    if mode == "1":
        cam_name = prompt_camera()
        mapping_json = CAMERA_MAPPINGS.get(cam_name)
        if not mapping_json or not os.path.exists(mapping_json):
            print(f"[WARNING] Mapping file for {cam_name} not found. Exiting.")
            return
        # Load zone and overlaps only for this camera
        global_zone, _ = load_global_zone_from_json(mapping_json)
        zone_polygons = {cam_name: global_zone['dst_points']}
        overlap_zones = {cam_name: global_zone['dst_points']}
        overlap_pairs = []
        tracker = CameraTracker(
            camera_name=cam_name,
            rtsp_url=CAMERA_RTSP[cam_name],
            mapping_json=mapping_json,
            offset=CAMERA_OFFSETS[cam_name],
            global_registry=registry,
            mall_map_img_path=floorplan_path,
            overlap_zones=overlap_zones,
            overlap_pairs=overlap_pairs
        )
        tracker.start()
        trackers.append(tracker)
    else:
        # Multi-camera mode: only use cameras with mapping files
        zone_polygons = {}
        for cam_key, mapping_json in CAMERA_MAPPINGS.items():
            cam_name = CAMERA_NUM_TO_NAME.get(cam_key, cam_key)
            if not os.path.exists(mapping_json):
                print(f"[WARNING] Mapping file {mapping_json} for {cam_name} not found. Skipping this camera.")
                continue
            global_zone, _ = load_global_zone_from_json(mapping_json)
            zone_polygons[cam_name] = global_zone['dst_points']
        # Compute overlaps
        overlap_pairs = []
        overlap_zones = {}
        for cam1, poly1 in zone_polygons.items():
            overlap_zones[cam1] = poly1
            for cam2, poly2 in zone_polygons.items():
                if cam1 >= cam2:
                    continue
                area, percent = compute_polygon_overlap(poly1, poly2)
                if area > 0.0:
                    overlap_pairs.append((cam1, cam2))
        for cam_name in zone_polygons:
            tracker = CameraTracker(
                camera_name=cam_name,
                rtsp_url=CAMERA_RTSP[cam_name],
                mapping_json=CAMERA_MAPPINGS[cam_name],
                offset=CAMERA_OFFSETS[cam_name],
                global_registry=registry,
                mall_map_img_path=floorplan_path,
                overlap_zones=overlap_zones,
                overlap_pairs=overlap_pairs
            )
            tracker.start()
            trackers.append(tracker)
    try:
        while any(t.is_alive() for t in trackers):
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all trackers...")
        for t in trackers:
            t.stop()
        for t in trackers:
            t.join()
    # --- Heatmap and bar graph generation after stream ends ---
    for cam_name in CAMERA_MAPPINGS:
        json_path = f"person_routes_{cam_name}.json"
        if os.path.exists(json_path):
            output_heatmap = f"heatmap_overlay_{cam_name}.png"
            output_person_object = f"person_object_interaction_{cam_name}.png"
            output_age_object = f"age_object_interaction_{cam_name}.png"
            generate_heatmap_from_routes(json_path, floorplan_path, output_heatmap)
            generate_person_object_interaction_bar(json_path, output_person_object)
            generate_age_object_interaction_bar(json_path, output_age_object)

if __name__ == "__main__":
    main() 