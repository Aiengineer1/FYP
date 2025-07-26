"""
Analytics Engine for AI Solutions
Provides analytics functionality for mall and camera data
"""

import os
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.crud import get_cameras_by_mall, get_mall, get_customer
from app.models.camera import Camera
from app.models.customer import Customer
from app.models.mall import Mall
import logging

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Dynamic analytics engine that pulls all data from database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_frontend_compatible_analytics(
        self,
        mall_id: int,
        time_range: str = "day",
        gender_filter: Optional[str] = None,
        age_filter: Optional[str] = None,
        zone_filter: Optional[str] = None,
        camera_filter: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a mall from database"""
        try:
            # Get mall and cameras
            mall = get_mall(self.db, mall_id)
            if not mall:
                return {"error": "Mall not found"}
            
            cameras = get_cameras_by_mall(self.db, mall_id)
            
            # Get time range
            start_time = self._get_start_time(time_range)
            
            # Get customers in time range
            customers = self._get_customers_in_range(mall_id, start_time)
            
            # Apply filters
            if gender_filter and gender_filter != "all":
                customers = [c for c in customers if c.gender == gender_filter]
            
            if age_filter:
                customers = self._filter_by_age_group(customers, age_filter)
            
            if zone_filter:
                customers = self._filter_by_zone(customers, zone_filter, cameras)
            
            if camera_filter:
                customers = self._filter_by_camera(customers, camera_filter)
            
            # Calculate analytics
            total_visitors = len(customers)
            active_visitors = len([c for c in customers if c.exit_time is None])
            
            # Calculate average dwell time
            dwell_times = []
            for customer in customers:
                if customer.entry_time and customer.exit_time:
                    dwell_time = (customer.exit_time - customer.entry_time).total_seconds() / 60
                    dwell_times.append(dwell_time)
            
            average_dwell_time = int(sum(dwell_times) / len(dwell_times)) if dwell_times else 0
            
            # Get popular sections from camera zones
            popular_sections = self._get_popular_sections(customers, cameras)
            
            # Get peak hours
            peak_hours = self._get_peak_hours(customers)
            
            return {
                "totalVisitors": total_visitors,
                "activeVisitors": active_visitors,
                "averageDwellTime": average_dwell_time,
                "peakHours": peak_hours,
                "popularSections": popular_sections
            }
            
        except Exception as e:
            logger.error(f"Error getting mall analytics: {str(e)}")
            return {"error": str(e)}
    
    def get_realtime_status(self, mall_id: int) -> Dict[str, Any]:
        """Get real-time status from database"""
        try:
            # Get active customers (no exit time)
            active_customers = self.db.query(Customer).filter(
                Customer.mall_id == mall_id,
                Customer.exit_time.is_(None)
            ).count()
            
            # Check if current time is peak hour
            current_hour = datetime.now().hour
            is_peak_hour = current_hour in [10, 11, 14, 15, 16, 17]  # Peak hours
            
            return {
                "activeVisitors": active_customers,
                "currentPeakHour": is_peak_hour,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting realtime status: {str(e)}")
            return {"error": str(e)}
    
    def get_heatmap_data(
        self,
        mall_id: int,
        time_range: str = "1h",
        gender_filter: Optional[str] = None,
        age_filter: Optional[str] = None,
        time_of_day: Optional[str] = None,
        zone_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get heatmap data from camera zones and customer data"""
        try:
            # Get mall and cameras with zones
            mall = get_mall(self.db, mall_id)
            cameras = get_cameras_by_mall(self.db, mall_id)
            
            # Get time range
            start_time = self._get_start_time(time_range)
            
            # Get customers in range
            customers = self._get_customers_in_range(mall_id, start_time)
            
            # Apply filters
            if gender_filter and gender_filter != "all":
                customers = [c for c in customers if c.gender == gender_filter]
            
            if age_filter:
                customers = self._filter_by_age_group(customers, age_filter)
            
            if time_of_day:
                customers = self._filter_by_time_of_day(customers, time_of_day)
            
            # Build zones from camera data
            zones = []
            for camera in cameras:
                if camera.fov_zones and camera.fov_zones.get("zones"):
                    for zone in camera.fov_zones["zones"]:
                        # Count customers in this zone
                        zone_customers = self._get_customers_in_zone(customers, zone, camera)
                        visitor_count = len(zone_customers)
                        
                        # Calculate density (0.0 to 1.0)
                        density = min(visitor_count / 50.0, 1.0) if visitor_count > 0 else 0.0
                        
                        zones.append({
                            "name": zone.get("name", f"Zone_{camera.id}"),
                            "visitorCount": visitor_count,
                            "coordinates": zone.get("src_points", []),  # Camera frame coordinates
                            "density": density
                        })
            
            return {
                "mallId": mall_id,
                "zones": zones,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting heatmap data: {str(e)}")
            return {"error": str(e)}
    
    def get_section_analytics(
        self,
        mall_id: int,
        time_range: str = "day",
        gender_filter: Optional[str] = None,
        age_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        rack_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get section/rack analytics from camera zones"""
        try:
            cameras = get_cameras_by_mall(self.db, mall_id)
            start_time = self._get_start_time(time_range)
            customers = self._get_customers_in_range(mall_id, start_time)
            
            # Apply filters
            if gender_filter and gender_filter != "all":
                customers = [c for c in customers if c.gender == gender_filter]
            
            if age_filter:
                customers = self._filter_by_age_group(customers, age_filter)
            
            sections = []
            
            for camera in cameras:
                if camera.fov_zones and camera.fov_zones.get("zones"):
                    for zone in camera.fov_zones["zones"]:
                        zone_name = zone.get("name", "")
                        
                        # Apply section filter
                        if section_filter and section_filter not in zone_name:
                            continue
                        
                        # Apply rack filter
                        if rack_filter and rack_filter not in zone_name:
                            continue
                        
                        # Get customers in this zone
                        zone_customers = self._get_customers_in_zone(customers, zone, camera)
                        
                        # Calculate demographics
                        male_count = len([c for c in zone_customers if c.gender == "male"])
                        female_count = len([c for c in zone_customers if c.gender == "female"])
                        total_count = len(zone_customers)
                        
                        # Calculate average dwell time for this zone
                        dwell_times = []
                        for customer in zone_customers:
                            if customer.entry_time and customer.exit_time:
                                dwell_time = (customer.exit_time - customer.entry_time).total_seconds() / 60
                                dwell_times.append(dwell_time)
                        
                        avg_dwell_time = int(sum(dwell_times) / len(dwell_times)) if dwell_times else 0
                        
                        sections.append({
                            "name": zone_name,
                            "section": zone_name.split("_")[0] if "_" in zone_name else zone_name,
                            "male": male_count,
                            "female": female_count,
                            "total": total_count,
                            "averageDwellTime": avg_dwell_time
                        })
            
            return sections
            
        except Exception as e:
            logger.error(f"Error getting section analytics: {str(e)}")
            return []
    
    def get_customer_insights(
        self,
        mall_id: int,
        time_range: str = "day",
        gender_filter: Optional[str] = None,
        age_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get customer demographics and insights from database"""
        try:
            start_time = self._get_start_time(time_range)
            customers = self._get_customers_in_range(mall_id, start_time)
            
            # Apply filters
            if gender_filter and gender_filter != "all":
                customers = [c for c in customers if c.gender == gender_filter]
            
            if age_filter:
                customers = self._filter_by_age_group(customers, age_filter)
            
            total = len(customers)
            male_count = len([c for c in customers if c.gender == "male"])
            female_count = len([c for c in customers if c.gender == "female"])
            
            # Calculate average age
            ages = [c.age for c in customers if c.age is not None]
            average_age = int(sum(ages) / len(ages)) if ages else 0
            
            # Age group distribution
            age_groups = {
                "18-25": len([c for c in customers if 18 <= c.age <= 25]),
                "26-35": len([c for c in customers if 26 <= c.age <= 35]),
                "36-45": len([c for c in customers if 36 <= c.age <= 45]),
                "46-55": len([c for c in customers if 46 <= c.age <= 55]),
                "55+": len([c for c in customers if c.age > 55])
            }
            
            return {
                "total": total,
                "male": male_count,
                "female": female_count,
                "averageAge": average_age,
                "ageGroups": age_groups
            }
            
        except Exception as e:
            logger.error(f"Error getting customer insights: {str(e)}")
            return {"error": str(e)}
    
    def get_camera_analytics(self, mall_id: int) -> List[Dict[str, Any]]:
        """Get camera analytics from database"""
        try:
            cameras = get_cameras_by_mall(self.db, mall_id)
            camera_analytics = []
            
            for camera in cameras:
                # Count customers tracked by this camera
                camera_customers = self.db.query(Customer).filter(
                    Customer.mall_id == mall_id,
                    Customer.routes.isnot(None)  # Has tracking data
                ).all()
                
                # Filter customers who visited zones from this camera
                camera_visitor_count = 0
                for customer in camera_customers:
                    if customer.visited_zones:
                        for zone_data in customer.visited_zones:
                            if zone_data.get("camera_id") == camera.id:
                                camera_visitor_count += 1
                                break
                
                # Determine health status based on zones and mappings
                health_status = "good"
                if not camera.fov_zones or not camera.fov_zones.get("zones"):
                    health_status = "warning"  # No zones configured
                if not camera.homography_map or not camera.homography_map.get("zones"):
                    health_status = "error"  # No mappings configured
                
                camera_analytics.append({
                    "id": camera.id,
                    "name": camera.name,
                    "location": camera.location,
                    "status": "active" if camera_visitor_count > 0 else "inactive",
                    "visitorCount": camera_visitor_count,
                    "lastActive": camera.created_at.isoformat() if camera.created_at else None,
                    "healthStatus": health_status
                })
            
            return camera_analytics
            
        except Exception as e:
            logger.error(f"Error getting camera analytics: {str(e)}")
            return []
    
    def get_alerts(
        self,
        mall_id: int,
        since: Optional[str] = None,
        zone_filter: Optional[str] = None,
        severity_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get alerts based on customer data and zone activity"""
        try:
            alerts = []
            
            # Get recent customers
            since_time = None
            if since:
                try:
                    since_time = datetime.fromisoformat(since.replace('Z', '+00:00'))
                except:
                    since_time = datetime.now() - timedelta(hours=1)
            else:
                since_time = datetime.now() - timedelta(hours=1)
            
            customers = self._get_customers_in_range(mall_id, since_time)
            cameras = get_cameras_by_mall(self.db, mall_id)
            
            # Check for high traffic alerts
            for camera in cameras:
                if camera.fov_zones and camera.fov_zones.get("zones"):
                    for zone in camera.fov_zones["zones"]:
                        zone_name = zone.get("name", "")
                        
                        # Apply zone filter
                        if zone_filter and zone_filter not in zone_name:
                            continue
                        
                        # Count customers in this zone
                        zone_customers = self._get_customers_in_zone(customers, zone, camera)
                        visitor_count = len(zone_customers)
                        
                        # Generate alerts based on thresholds
                        if visitor_count > 30:  # High traffic
                            alerts.append({
                                "id": len(alerts) + 1,
                                "type": "high_traffic",
                                "message": f"High traffic detected in {zone_name} section",
                                "severity": "warning",
                                "zone": zone_name,
                                "time": datetime.now().isoformat()
                            })
                        
                        if visitor_count > 50:  # Very high traffic
                            alerts.append({
                                "id": len(alerts) + 1,
                                "type": "very_high_traffic",
                                "message": f"Very high traffic detected in {zone_name} section",
                                "severity": "error",
                                "zone": zone_name,
                                "time": datetime.now().isoformat()
                            })
            
            # Apply severity filter
            if severity_filter:
                alerts = [a for a in alerts if a["severity"] == severity_filter]
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            return []
    
    def get_timeseries_data(
        self,
        mall_id: int,
        metric: str = "visitors",
        time_range: str = "day",
        zone_filter: Optional[str] = None,
        camera_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get time series data for graphs"""
        try:
            start_time = self._get_start_time(time_range)
            customers = self._get_customers_in_range(mall_id, start_time)
            cameras = get_cameras_by_mall(self.db, mall_id)
            
            # Apply filters
            if zone_filter:
                customers = self._filter_by_zone(customers, zone_filter, cameras)
            
            if camera_filter:
                customers = self._filter_by_camera(customers, camera_filter)
            
            # Group by hour
            hourly_data = {}
            for customer in customers:
                if customer.entry_time:
                    hour = customer.entry_time.strftime("%H:00")
                    if hour not in hourly_data:
                        hourly_data[hour] = {"visitors": 0, "interactions": 0}
                    
                    hourly_data[hour]["visitors"] += 1
                    
                    # Count interactions from customer data
                    if customer.interactions:
                        hourly_data[hour]["interactions"] += len(customer.interactions)
            
            # Convert to list format
            timeseries = []
            for hour in sorted(hourly_data.keys()):
                data = hourly_data[hour]
                timeseries.append({
                    "time": hour,
                    "visitors": data["visitors"],
                    "interactions": data["interactions"]
                })
            
            return timeseries
            
        except Exception as e:
            logger.error(f"Error getting timeseries data: {str(e)}")
            return []
    
    # Helper methods
    def _get_start_time(self, time_range: str) -> datetime:
        """Get start time based on range"""
        now = datetime.now()
        if time_range == "hour":
            return now - timedelta(hours=1)
        elif time_range == "day":
            return now - timedelta(days=1)
        elif time_range == "week":
            return now - timedelta(weeks=1)
        elif time_range == "month":
            return now - timedelta(days=30)
        else:
            return now - timedelta(days=1)
    
    def _get_customers_in_range(self, mall_id: int, start_time: datetime) -> List[Customer]:
        """Get customers within time range"""
        return self.db.query(Customer).filter(
            Customer.mall_id == mall_id,
            Customer.entry_time >= start_time
        ).all()
    
    def _filter_by_age_group(self, customers: List[Customer], age_filter: str) -> List[Customer]:
        """Filter customers by age group"""
        if age_filter == "18-25":
            return [c for c in customers if 18 <= c.age <= 25]
        elif age_filter == "26-35":
            return [c for c in customers if 26 <= c.age <= 35]
        elif age_filter == "36-45":
            return [c for c in customers if 36 <= c.age <= 45]
        elif age_filter == "46-55":
            return [c for c in customers if 46 <= c.age <= 55]
        elif age_filter == "55+":
            return [c for c in customers if c.age > 55]
        return customers
    
    def _filter_by_zone(self, customers: List[Customer], zone_filter: str, cameras: List[Camera]) -> List[Customer]:
        """Filter customers by zone"""
        filtered_customers = []
        for customer in customers:
            if customer.visited_zones:
                for zone_data in customer.visited_zones:
                    zone_name = zone_data.get("zone_name", "")
                    if zone_filter.lower() in zone_name.lower():
                        filtered_customers.append(customer)
                        break
        return filtered_customers
    
    def _filter_by_camera(self, customers: List[Customer], camera_filter: int) -> List[Customer]:
        """Filter customers by camera"""
        filtered_customers = []
        for customer in customers:
            if customer.visited_zones:
                for zone_data in customer.visited_zones:
                    if zone_data.get("camera_id") == camera_filter:
                        filtered_customers.append(customer)
                        break
        return filtered_customers
    
    def _filter_by_time_of_day(self, customers: List[Customer], time_of_day: str) -> List[Customer]:
        """Filter customers by time of day"""
        filtered_customers = []
        for customer in customers:
            if customer.entry_time:
                hour = customer.entry_time.hour
                if time_of_day == "morning" and 6 <= hour < 12:
                    filtered_customers.append(customer)
                elif time_of_day == "afternoon" and 12 <= hour < 17:
                    filtered_customers.append(customer)
                elif time_of_day == "evening" and 17 <= hour < 21:
                    filtered_customers.append(customer)
                elif time_of_day == "night" and (hour >= 21 or hour < 6):
                    filtered_customers.append(customer)
        return filtered_customers
    
    def _get_customers_in_zone(self, customers: List[Customer], zone: Dict, camera: Camera) -> List[Customer]:
        """Get customers who visited a specific zone"""
        zone_customers = []
        zone_name = zone.get("name", "")
        
        for customer in customers:
            if customer.visited_zones:
                for zone_data in customer.visited_zones:
                    if (zone_data.get("zone_name") == zone_name and 
                        zone_data.get("camera_id") == camera.id):
                        zone_customers.append(customer)
                        break
        
        return zone_customers
    
    def _get_popular_sections(self, customers: List[Customer], cameras: List[Camera]) -> List[Dict[str, Any]]:
        """Get popular sections based on zone visits"""
        section_counts = {}
        
        for customer in customers:
            if customer.visited_zones:
                for zone_data in customer.visited_zones:
                    zone_name = zone_data.get("zone_name", "")
                    if zone_name:
                        section_name = zone_name.split("_")[0] if "_" in zone_name else zone_name
                        section_counts[section_name] = section_counts.get(section_name, 0) + 1
        
        # Convert to list and sort by count
        popular_sections = [
            {"name": section, "visitorCount": count}
            for section, count in sorted(section_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return popular_sections[:5]  # Top 5 sections
    
    def _get_peak_hours(self, customers: List[Customer]) -> List[str]:
        """Get peak hours based on customer entry times"""
        hourly_counts = {}
        
        for customer in customers:
            if customer.entry_time:
                hour = customer.entry_time.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        # Find hours with highest counts
        if hourly_counts:
            max_count = max(hourly_counts.values())
            peak_hours = [
                f"{hour:02d}:00-{(hour+1):02d}:00"
                for hour, count in hourly_counts.items()
                if count >= max_count * 0.8  # Within 80% of peak
            ]
            return sorted(peak_hours)
        
        return [] 