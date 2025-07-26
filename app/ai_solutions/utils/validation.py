"""
Validation utilities for AI solutions
Common validation functions and data validation
"""

import re
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

class ValidationUtils:
    """Utility class for common validation functions"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_rtsp_url(url: str) -> bool:
        """Validate RTSP URL format"""
        pattern = r'^rtsp://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address format"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    @staticmethod
    def validate_port(port: Union[str, int]) -> bool:
        """Validate port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_camera_id(camera_id: str) -> bool:
        """Validate camera ID format"""
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, camera_id))
    
    @staticmethod
    def validate_json_structure(data: Dict, required_keys: List[str]) -> bool:
        """Validate that JSON data contains required keys"""
        return all(key in data for key in required_keys)
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file extension"""
        return any(filename.lower().endswith(ext.lower()) for ext in allowed_extensions)
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: float, max_val: float) -> bool:
        """Validate numeric value is within range"""
        try:
            num_val = float(value)
            return min_val <= num_val <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_string_length(text: str, min_length: int = 0, max_length: int = None) -> bool:
        """Validate string length"""
        if not isinstance(text, str):
            return False
        
        if len(text) < min_length:
            return False
        
        if max_length is not None and len(text) > max_length:
            return False
        
        return True
    
    @staticmethod
    def validate_list_not_empty(data: List) -> bool:
        """Validate that list is not empty"""
        return isinstance(data, list) and len(data) > 0
    
    @staticmethod
    def validate_dict_not_empty(data: Dict) -> bool:
        """Validate that dictionary is not empty"""
        return isinstance(data, dict) and len(data) > 0
    
    @staticmethod
    def validate_path_exists(path: Union[str, Path]) -> bool:
        """Validate that file or directory path exists"""
        return Path(path).exists()
    
    @staticmethod
    def validate_file_exists(filepath: Union[str, Path]) -> bool:
        """Validate that file exists"""
        path = Path(filepath)
        return path.exists() and path.is_file()
    
    @staticmethod
    def validate_directory_exists(dirpath: Union[str, Path]) -> bool:
        """Validate that directory exists"""
        path = Path(dirpath)
        return path.exists() and path.is_dir()
    
    @staticmethod
    def validate_model_config(config: Dict) -> Dict[str, Any]:
        """Validate model configuration"""
        errors = []
        warnings = []
        
        required_fields = ['model_path', 'model_type', 'input_size']
        
        # Check required fields
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate model path
        if 'model_path' in config:
            if not ValidationUtils.validate_file_exists(config['model_path']):
                errors.append(f"Model file not found: {config['model_path']}")
        
        # Validate input size
        if 'input_size' in config:
            input_size = config['input_size']
            if not isinstance(input_size, (list, tuple)) or len(input_size) != 3:
                errors.append("Input size must be a list/tuple of 3 elements [height, width, channels]")
            elif not all(isinstance(x, int) and x > 0 for x in input_size):
                errors.append("Input size elements must be positive integers")
        
        # Validate confidence threshold
        if 'confidence_threshold' in config:
            if not ValidationUtils.validate_numeric_range(config['confidence_threshold'], 0.0, 1.0):
                errors.append("Confidence threshold must be between 0.0 and 1.0")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_camera_config(config: Dict) -> Dict[str, Any]:
        """Validate camera configuration"""
        errors = []
        warnings = []
        
        required_fields = ['camera_id', 'rtsp_url', 'position']
        
        # Check required fields
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate camera ID
        if 'camera_id' in config:
            if not ValidationUtils.validate_camera_id(config['camera_id']):
                errors.append(f"Invalid camera ID format: {config['camera_id']}")
        
        # Validate RTSP URL
        if 'rtsp_url' in config:
            if not ValidationUtils.validate_rtsp_url(config['rtsp_url']):
                warnings.append(f"Invalid RTSP URL format: {config['rtsp_url']}")
        
        # Validate position coordinates
        if 'position' in config:
            position = config['position']
            if not isinstance(position, (list, tuple)) or len(position) != 2:
                errors.append("Position must be a list/tuple of 2 elements [x, y]")
            elif not all(isinstance(x, (int, float)) for x in position):
                errors.append("Position coordinates must be numeric")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }