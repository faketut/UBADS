import os
from typing import Dict, Any

class Config:
    """Configuration class for the User Behavior Anomaly Detection System"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'log', 'csv'}
    
    # Anomaly Detection Configuration
    DEFAULT_THRESHOLD = 0.6
    DEFAULT_CONTAMINATION = 0.1
    DEFAULT_N_ESTIMATORS = 100
    DEFAULT_RANDOM_STATE = 42
    
    # Sample Data Configuration
    DEFAULT_NUM_USERS = 50
    DEFAULT_LOGS_PER_USER = 100
    
    # Feature Extraction Configuration
    FEATURE_CONFIG = {
        'time_based_features': True,
        'action_based_features': True,
        'resource_based_features': True,
        'status_based_features': True,
        'response_time_features': True,
        'ip_based_features': True,
        'session_based_features': True
    }
    
    # Log Patterns Configuration
    LOG_PATTERNS = {
        'timestamp': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
        'user_id': r'user[_:](\w+)',
        'ip_address': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
        'action': r'(GET|POST|PUT|DELETE|LOGIN|LOGOUT|FAILED_LOGIN)',
        'resource': r'/([\w/.-]+)',
        'status_code': r'status[_:](\d{3})',
        'response_time': r'time[_:](\d+)ms'
    }
    
    # UI Configuration
    UI_CONFIG = {
        'theme': 'light',  # 'light' or 'dark'
        'charts_enabled': True,
        'real_time_updates': False,
        'max_display_users': 50,
        'auto_refresh_interval': 30000  # 30 seconds
    }
    
    # Database Configuration (for future use)
    DATABASE_CONFIG = {
        'enabled': False,
        'type': 'sqlite',  # 'sqlite', 'postgresql', 'mysql'
        'url': os.environ.get('DATABASE_URL', 'sqlite:///anomaly_detection.db')
    }
    
    # Security Configuration
    SECURITY_CONFIG = {
        'enable_authentication': False,
        'session_timeout': 3600,  # 1 hour
        'max_login_attempts': 5,
        'password_min_length': 8
    }
    
    # Notification Configuration
    NOTIFICATION_CONFIG = {
        'email_notifications': False,
        'webhook_notifications': False,
        'webhook_url': os.environ.get('WEBHOOK_URL', ''),
        'notification_threshold': 0.8
    }
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all configuration as a dictionary"""
        return {
            'flask': {
                'secret_key': cls.SECRET_KEY,
                'debug': cls.DEBUG,
                'host': cls.HOST,
                'port': cls.PORT
            },
            'upload': {
                'upload_folder': cls.UPLOAD_FOLDER,
                'max_content_length': cls.MAX_CONTENT_LENGTH,
                'allowed_extensions': list(cls.ALLOWED_EXTENSIONS)
            },
            'anomaly_detection': {
                'default_threshold': cls.DEFAULT_THRESHOLD,
                'default_contamination': cls.DEFAULT_CONTAMINATION,
                'default_n_estimators': cls.DEFAULT_N_ESTIMATORS,
                'default_random_state': cls.DEFAULT_RANDOM_STATE
            },
            'sample_data': {
                'default_num_users': cls.DEFAULT_NUM_USERS,
                'default_logs_per_user': cls.DEFAULT_LOGS_PER_USER
            },
            'feature_config': cls.FEATURE_CONFIG,
            'log_patterns': cls.LOG_PATTERNS,
            'ui_config': cls.UI_CONFIG,
            'database_config': cls.DATABASE_CONFIG,
            'security_config': cls.SECURITY_CONFIG,
            'notification_config': cls.NOTIFICATION_CONFIG
        }
    
    @classmethod
    def update_config(cls, config_updates: Dict[str, Any]) -> None:
        """Update configuration values"""
        for section, values in config_updates.items():
            if hasattr(cls, section.upper()):
                section_attr = getattr(cls, section.upper())
                if isinstance(section_attr, dict):
                    section_attr.update(values)
                else:
                    setattr(cls, section.upper(), values) 