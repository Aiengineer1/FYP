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
            return 0.0, 0.0, 0.0, 'invalid'
        inter = p1.intersection(p2)
        if inter.is_empty:
            return 0.0, 0.0, 0.0, 'no_overlap'
        overlap_area = inter.area
        percent1 = overlap_area / p1.area if p1.area > 0 else 0.0
        percent2 = overlap_area / p2.area if p2.area > 0 else 0.0
        
        # Calculate overlap quality metrics
        union_area = p1.union(p2).area
        iou = overlap_area / union_area if union_area > 0 else 0.0
        
        # Determine overlap quality
        if iou > 0.7:
            quality = 'high'
        elif iou > 0.3:
            quality = 'medium'
        elif iou > 0.1:
            quality = 'low'
        else:
            quality = 'minimal'
            
        return overlap_area, min(percent1, percent2), iou, quality
    else:
        # Fallback: no overlap calculation
        return 0.0, 0.0, 0.0, 'unknown'

def analyze_camera_overlaps(zone_polygons, min_overlap_area=100.0, min_overlap_percent=0.05):
    """
    Analyze overlaps between all camera zones and return quality metrics
    
    Args:
        zone_polygons: dict of camera_name -> polygon_points
        min_overlap_area: minimum overlap area to consider significant
        min_overlap_percent: minimum overlap percentage to consider significant
    
    Returns:
        overlap_pairs: list of (cam1, cam2) pairs with significant overlap
        overlap_zones: dict of camera_name -> polygon_points
        overlap_metrics: dict of (cam1, cam2) -> overlap_info
    """
    overlap_pairs = []
    overlap_zones = {}
    overlap_metrics = {}
    
    camera_names = list(zone_polygons.keys())
    
    for i, cam1 in enumerate(camera_names):
        overlap_zones[cam1] = zone_polygons[cam1]  # Each camera's own zone
        
        for j, cam2 in enumerate(camera_names):
            if i >= j:  # Skip self and already processed pairs
                continue
                
            poly1 = zone_polygons[cam1]
            poly2 = zone_polygons[cam2]
            
            area, percent, iou, quality = compute_polygon_overlap(poly1, poly2)
            
            # Check if overlap is significant
            is_significant = (area > min_overlap_area and percent > min_overlap_percent)
            
            overlap_metrics[(cam1, cam2)] = {
                'overlap_area': area,
                'overlap_percent': percent,
                'iou': iou,
                'quality': quality,
                'is_significant': is_significant
            }
            
            if is_significant:
                overlap_pairs.append((cam1, cam2))
                print(f"[ZoneUtils] Significant overlap detected: {cam1} ↔ {cam2}")
                print(f"  - Overlap area: {area:.2f}")
                print(f"  - Overlap percent: {percent:.3f}")
                print(f"  - IoU: {iou:.3f}")
                print(f"  - Quality: {quality}")
    
    return overlap_pairs, overlap_zones, overlap_metrics

def get_overlap_zone_center(overlap_metrics, cam1, cam2):
    """Get the center point of the overlap zone between two cameras"""
    if (cam1, cam2) in overlap_metrics:
        # This would require computing the actual intersection polygon
        # For now, return a simple midpoint
        return None
    return None

def validate_zone_configuration(zone_polygons, overlap_metrics):
    """
    Validate the zone configuration and provide recommendations
    
    Returns:
        dict with validation results and recommendations
    """
    validation_results = {
        'total_cameras': len(zone_polygons),
        'significant_overlaps': 0,
        'high_quality_overlaps': 0,
        'isolated_cameras': [],
        'recommendations': []
    }
    
    # Count overlaps
    for (cam1, cam2), metrics in overlap_metrics.items():
        if metrics['is_significant']:
            validation_results['significant_overlaps'] += 1
        if metrics['quality'] == 'high':
            validation_results['high_quality_overlaps'] += 1
    
    # Find isolated cameras (no significant overlaps)
    all_cameras = set(zone_polygons.keys())
    cameras_with_overlaps = set()
    
    for (cam1, cam2), metrics in overlap_metrics.items():
        if metrics['is_significant']:
            cameras_with_overlaps.add(cam1)
            cameras_with_overlaps.add(cam2)
    
    validation_results['isolated_cameras'] = list(all_cameras - cameras_with_overlaps)
    
    # Generate recommendations
    if validation_results['significant_overlaps'] == 0:
        validation_results['recommendations'].append(
            "No significant overlaps detected. Consider adjusting camera zones for better person tracking."
        )
    
    if validation_results['isolated_cameras']:
        validation_results['recommendations'].append(
            f"Cameras {validation_results['isolated_cameras']} have no overlaps. "
            "They will work independently but won't share person IDs."
        )
    
    if validation_results['high_quality_overlaps'] < len(zone_polygons) - 1:
        validation_results['recommendations'].append(
            "Consider improving zone overlap quality for better cross-camera person matching."
        )
    
    return validation_results 