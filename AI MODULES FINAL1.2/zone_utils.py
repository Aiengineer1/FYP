import json
import numpy as np
import cv2
try:
    from shapely.geometry import Polygon
except ImportError:
    Polygon = None

def load_global_zone_from_json(json_path):
    with open(json_path, 'r') as f:
        objects = json.load(f)
    global_zone = None
    for obj in objects:
        if obj['name'] == 'global_zone':
            global_zone = obj
            break
    if global_zone is None:
        raise ValueError(f"No global_zone found in {json_path}")
    src_pts = np.array(global_zone['src_points'], dtype=np.float32)
    dst_pts = np.array(global_zone['dst_points'], dtype=np.float32)
    H, _ = cv2.findHomography(src_pts, dst_pts, method=0)
    return global_zone, H

def transform_points(points, H):
    pts = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    mapped = cv2.perspectiveTransform(pts, H)
    return mapped.reshape(-1, 2)

def point_in_polygon(point, polygon):
    # polygon: list of (x, y)
    contour = np.array(polygon, dtype=np.int32)
    return cv2.pointPolygonTest(contour, (float(point[0]), float(point[1])), False) >= 0

def compute_polygon_overlap(poly1, poly2):
    # poly1, poly2: list of (x, y)
    if Polygon is not None:
        p1 = Polygon(poly1)
        p2 = Polygon(poly2)
        if not p1.is_valid or not p2.is_valid:
            return 0.0, 0.0
        inter = p1.intersection(p2)
        if inter.is_empty:
            return 0.0, 0.0
        overlap_area = inter.area
        percent1 = overlap_area / p1.area if p1.area > 0 else 0.0
        percent2 = overlap_area / p2.area if p2.area > 0 else 0.0
        return overlap_area, min(percent1, percent2)
    else:
        # Fallback: no overlap calculation
        return 0.0, 0.0 