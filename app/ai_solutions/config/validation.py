"""
Configuration validation module for AI solutions
Validates model paths, camera configurations, and system settings
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class ConfigValidator:
    """Validates AI system configuration settings"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.errors = []
        self.warnings = []
    
    def validate_model_paths(self, model_paths: Dict[str, str]) -> bool:
        """Validate that all model files exist"""
        is_valid = True
        
        for model_name, model_path in model_paths.items():
            full_path = self.config_dir.parent / model_path
            if not full_path.exists():
                self.errors.append(f"Model file not found: {model_path} for {model_name}")
                is_valid = False
            elif full_path.stat().st_size == 0:
                self.warnings.append(f"Model file is empty: {model_path} for {model_name}")
        
        return is_valid
    
    def validate_camera_config(self, camera_config: Dict) -> bool:
        """Validate camera configuration settings"""
        is_valid = True
        required_fields = ['rtsp_urls', 'mappings', 'offsets']
        
        for field in required_fields:
            if field not in camera_config:
                self.errors.append(f"Missing required camera config field: {field}")
                is_valid = False
        
        # Validate RTSP URLs
        if 'rtsp_urls' in camera_config:
            for cam_name, url in camera_config['rtsp_urls'].items():
                if not url.startswith(('rtsp://', 'http://', 'https://')):
                    self.warnings.append(f"Invalid RTSP URL format for {cam_name}: {url}")
        
        return is_valid
    
    def validate_analytics_paths(self, analytics_config: Dict) -> bool:
        """Validate analytics output paths"""
        is_valid = True
        
        analytics_dir = Path(analytics_config.get('output_dir', 'analytics'))
        if not analytics_dir.exists():
            try:
                analytics_dir.mkdir(parents=True, exist_ok=True)
                self.warnings.append(f"Created analytics directory: {analytics_dir}")
            except Exception as e:
                self.errors.append(f"Cannot create analytics directory: {e}")
                is_valid = False
        
        return is_valid
    
    def validate_system_requirements(self) -> bool:
        """Validate system requirements and dependencies"""
        is_valid = True
        
        # Check for required directories
        required_dirs = ['ml_models', 'config', 'core', 'assets']
        for dir_name in required_dirs:
            dir_path = self.config_dir.parent / dir_name
            if not dir_path.exists():
                self.errors.append(f"Required directory missing: {dir_name}")
                is_valid = False
        
        return is_valid
    
    def get_validation_summary(self) -> Dict:
        """Get a summary of validation results"""
        return {
            'is_valid': len(self.errors) == 0,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def print_validation_report(self):
        """Print validation results to console"""
        summary = self.get_validation_summary()
        
        print("=== Configuration Validation Report ===")
        print(f"Status: {'✅ PASSED' if summary['is_valid'] else '❌ FAILED'}")
        print(f"Errors: {summary['error_count']}")
        print(f"Warnings: {summary['warning_count']}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("=" * 40)

class ErrorHandler:
    """Centralized error handling for AI system"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.error_count = 0
        self.warning_count = 0
    
    def handle_model_error(self, error: Exception, model_name: str) -> bool:
        """Handle model loading/initialization errors"""
        self.error_count += 1
        error_msg = f"Model error for {model_name}: {str(error)}"
        
        print(f"❌ {error_msg}")
        if self.log_file:
            self._log_error(error_msg)
        
        return False
    
    def handle_camera_error(self, error: Exception, camera_name: str) -> bool:
        """Handle camera connection/streaming errors"""
        self.error_count += 1
        error_msg = f"Camera error for {camera_name}: {str(error)}"
        
        print(f"❌ {error_msg}")
        if self.log_file:
            self._log_error(error_msg)
        
        return False
    
    def handle_analytics_error(self, error: Exception, operation: str) -> bool:
        """Handle analytics generation errors"""
        self.error_count += 1
        error_msg = f"Analytics error during {operation}: {str(error)}"
        
        print(f"❌ {error_msg}")
        if self.log_file:
            self._log_error(error_msg)
        
        return False
    
    def handle_warning(self, message: str) -> None:
        """Handle warnings"""
        self.warning_count += 1
        warning_msg = f"⚠️  WARNING: {message}"
        
        print(warning_msg)
        if self.log_file:
            self._log_warning(message)
    
    def _log_error(self, message: str) -> None:
        """Log error to file"""
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"ERROR: {message}\n")
    
    def _log_warning(self, message: str) -> None:
        """Log warning to file"""
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"WARNING: {message}\n")
    
    def get_error_summary(self) -> Dict:
        """Get error handling summary"""
        return {
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'has_errors': self.error_count > 0
        } 