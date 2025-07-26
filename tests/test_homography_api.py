import cv2
import numpy as np

# --- Helper for mouse click ---
def select_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        param.append((x, y))
        print(f"Point selected: ({x}, {y})")

def get_points(image, window_name):
    points = []
    cv2.imshow(window_name, image)
    cv2.setMouseCallback(window_name, select_points, points)
    print(f"Select 4 points on {window_name} (in order: top-left, top-right, bottom-right, bottom-left)")
    while len(points) < 4:
        cv2.waitKey(1)
    cv2.destroyWindow(window_name)
    return np.array(points, dtype=np.float32)

if __name__ == "__main__":
    # --- Load local images ---
    mall_map_img = cv2.imread("floorplan_gui.png")
    camera_img = cv2.imread("camera_frame.png")

    if camera_img is None or mall_map_img is None:
        print("Error: Could not load images. Make sure 'floorplan_gui.png' and 'camera_frame.png' exist in the current directory.")
        exit(1)

    # Resize both images to 1280x720 for consistency (optional)
    camera_img = cv2.resize(camera_img, (1280, 720))
    mall_map_img = cv2.resize(mall_map_img, (1280, 720))

    # Select points
    src_points = get_points(camera_img, "Select on Camera Frame")
    dst_points = get_points(mall_map_img, "Select on Mall Map")

    print("Camera Frame Points:", src_points)
    print("Mall Map Points:", dst_points)

    # Compute homography (warp mall map onto camera frame)
    H, status = cv2.findHomography(dst_points, src_points, method=cv2.RANSAC)
    print("Homography Matrix:\n", H)

    # Warp mall map to camera frame perspective
    warped_map = cv2.warpPerspective(mall_map_img, H, (1280, 720))

    # Create mask for the selected polygon (on camera frame)
    mask = np.zeros_like(camera_img, dtype=np.uint8)
    cv2.fillConvexPoly(mask, np.int32(src_points), (255, 255, 255))

    # Masked warped map (only inside polygon)
    masked_warped = cv2.bitwise_and(warped_map, mask)

    # Blend masked warped map with camera frame
    blended = cv2.addWeighted(camera_img, 1, masked_warped, 0.6, 0)

    # Draw polygon outline on blended image
    cv2.polylines(blended, [np.int32(src_points)], True, (0, 255, 0), 2)

    # Show results
    cv2.imshow("Mall Map Warped onto Camera Frame (Backend Logic)", blended)
    cv2.waitKey(0)
    cv2.destroyAllWindows() 