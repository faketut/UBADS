import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import json
import re
import logging
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogPreprocessor:
    """Handles log file preprocessing and user-based organization"""
    
    def __init__(self):
        self.user_logs = defaultdict(list)
        self.log_patterns = {
            'timestamp': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            'user_id': r'user[_:](\w+)',
            'ip_address': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
            'action': r'(GET|POST|PUT|DELETE|LOGIN|LOGOUT|FAILED_LOGIN)',
            'resource': r'/([\w/.-]+)',
            'status_code': r'status[_:](\d{3})',
            'response_time': r'time[_:](\d+)ms'
        }
    
    def parse_log_line(self, log_line: str) -> Dict[str, Any]:
        """Parse a single log line and extract relevant information"""
        parsed_data = {}
        
        for field, pattern in self.log_patterns.items():
            match = re.search(pattern, log_line, re.IGNORECASE)
            if match:
                if field == 'timestamp':
                    try:
                        parsed_data[field] = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        parsed_data[field] = None
                elif field in ['status_code', 'response_time']:
                    parsed_data[field] = int(match.group(1))
                else:
                    parsed_data[field] = match.group(1)
            else:
                parsed_data[field] = None
        
        # Add raw log line for reference
        parsed_data['raw_log'] = log_line.strip()
        
        return parsed_data
    
    def preprocess_log_files(self, log_files: List[str]) -> Dict[str, List[Dict]]:
        """Process multiple log files and organize by user"""
        logger.info("Starting log preprocessing...")
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        if line.strip():  # Skip empty lines
                            parsed_log = self.parse_log_line(line)
                            user_id = parsed_log.get('user_id')
                            
                            if user_id:
                                self.user_logs[user_id].append(parsed_log)
                            
            except FileNotFoundError:
                logger.warning(f"Log file not found: {log_file}")
            except Exception as e:
                logger.error(f"Error processing {log_file}: {str(e)}")
        
        logger.info(f"Processed logs for {len(self.user_logs)} users")
        return dict(self.user_logs)
    
    def create_sample_logs(self, num_users: int = 50, logs_per_user: int = 100) -> List[str]:
        """Generate sample log data for demonstration"""
        sample_logs = []
        actions = ['GET', 'POST', 'PUT', 'DELETE', 'LOGIN', 'LOGOUT', 'FAILED_LOGIN']
        resources = ['/api/data', '/login', '/dashboard', '/profile', '/settings', '/admin']
        status_codes = [200, 201, 400, 401, 403, 404, 500]
        
        for user_id in range(1, num_users + 1):
            user_name = f"user{user_id:03d}"
            
            # Create baseline behavior for most users
            is_anomalous = np.random.random() < 0.1  # 10% anomalous users
            
            for log_id in range(logs_per_user):
                timestamp = datetime.now() - timedelta(
                    days=np.random.randint(0, 30),
                    hours=np.random.randint(0, 24),
                    minutes=np.random.randint(0, 60)
                )
                
                if is_anomalous and np.random.random() < 0.3:
                    # Anomalous behavior patterns
                    action = np.random.choice(['FAILED_LOGIN', 'DELETE', 'GET'])
                    resource = np.random.choice(['/admin', '/sensitive', '/api/data'])
                    status_code = np.random.choice([401, 403, 404, 500])
                    response_time = np.random.randint(5000, 15000)  # Very slow
                    ip = f"192.168.{np.random.randint(100, 200)}.{np.random.randint(1, 255)}"
                else:
                    # Normal behavior
                    action = np.random.choice(actions[:5])  # Avoid failed logins mostly
                    resource = np.random.choice(resources[:4])  # Avoid admin
                    status_code = np.random.choice([200, 201, 400])
                    response_time = np.random.randint(100, 2000)  # Normal response time
                    ip = f"192.168.1.{np.random.randint(1, 100)}"
                
                log_entry = (
                    f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"user:{user_name} {ip} {action} {resource} "
                    f"status:{status_code} time:{response_time}ms"
                )
                sample_logs.append(log_entry)
        
        # Save sample logs to file
        with open('sample_logs.txt', 'w') as f:
            f.write('\n'.join(sample_logs))
        
        return ['sample_logs.txt']

class UserFeatureExtractor:
    """Extracts features from user-specific log data"""
    
    def __init__(self):
        self.feature_names = []
    
    def extract_user_features(self, user_logs: List[Dict]) -> Dict[str, float]:
        """Extract features for a specific user"""
        if not user_logs:
            return {}
        
        features = {}
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(user_logs)
        
        # Time-based features
        features['total_logs'] = len(user_logs)
        features['unique_days'] = len(df['timestamp'].dt.date.unique()) if 'timestamp' in df.columns else 0
        features['avg_logs_per_day'] = features['total_logs'] / max(features['unique_days'], 1)
        
        # Activity time features
        if 'timestamp' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            features['night_activity_ratio'] = len(df[(df['hour'] >= 22) | (df['hour'] <= 6)]) / len(df)
            features['weekend_activity_ratio'] = len(df[df['timestamp'].dt.weekday >= 5]) / len(df)
        
        # Action-based features
        if 'action' in df.columns:
            action_counts = df['action'].value_counts()
            features['failed_login_ratio'] = action_counts.get('FAILED_LOGIN', 0) / len(df)
            features['delete_ratio'] = action_counts.get('DELETE', 0) / len(df)
            features['admin_action_ratio'] = action_counts.get('POST', 0) / len(df)
            features['unique_actions'] = len(action_counts)
        
        # Resource access features
        if 'resource' in df.columns:
            resource_counts = df['resource'].value_counts()
            features['unique_resources'] = len(resource_counts)
            features['admin_access_ratio'] = len(df[df['resource'].str.contains('/admin', na=False)]) / len(df)
            features['resource_diversity'] = len(resource_counts) / len(df)
        
        # Status code features
        if 'status_code' in df.columns:
            status_counts = df['status_code'].value_counts()
            features['error_rate'] = len(df[df['status_code'] >= 400]) / len(df)
            features['success_rate'] = len(df[df['status_code'] < 400]) / len(df)
            features['unique_status_codes'] = len(status_counts)
        
        # Response time features
        if 'response_time' in df.columns:
            response_times = df['response_time'].dropna()
            if len(response_times) > 0:
                features['avg_response_time'] = response_times.mean()
                features['max_response_time'] = response_times.max()
                features['response_time_std'] = response_times.std()
                features['slow_requests_ratio'] = len(response_times[response_times > 5000]) / len(response_times)
        
        # IP address features
        if 'ip_address' in df.columns:
            ip_counts = df['ip_address'].value_counts()
            features['unique_ips'] = len(ip_counts)
            features['ip_diversity'] = len(ip_counts) / len(df)
        
        # Session-based features (approximate)
        if 'timestamp' in df.columns:
            df_sorted = df.sort_values('timestamp')
            time_diffs = df_sorted['timestamp'].diff().dt.total_seconds()
            features['avg_session_length'] = time_diffs.mean() if len(time_diffs) > 1 else 0
            features['max_idle_time'] = time_diffs.max() if len(time_diffs) > 1 else 0
        
        # Fill NaN values with 0
        for key, value in features.items():
            if pd.isna(value):
                features[key] = 0.0
        
        return features
    
    def extract_all_features(self, user_logs_dict: Dict[str, List[Dict]]) -> pd.DataFrame:
        """Extract features for all users"""
        logger.info("Extracting features for all users...")
        
        feature_data = []
        
        for user_id, logs in user_logs_dict.items():
            user_features = self.extract_user_features(logs)
            user_features['user_id'] = user_id
            feature_data.append(user_features)
        
        feature_df = pd.DataFrame(feature_data)
        
        # Store feature names for later use
        self.feature_names = [col for col in feature_df.columns if col != 'user_id']
        
        logger.info(f"Extracted {len(self.feature_names)} features for {len(feature_df)} users")
        
        return feature_df

class ExtendedIsolationForest:
    """Extended Isolation Forest implementation for anomaly detection"""
    
    def __init__(self, contamination=0.1, n_estimators=100, random_state=42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_fitted = False
    
    def fit(self, X: pd.DataFrame, feature_names: List[str]):
        """Train the Extended Isolation Forest model"""
        logger.info("Training Extended Isolation Forest model...")
        
        # Remove user_id column if present
        if 'user_id' in X.columns:
            X_features = X.drop('user_id', axis=1)
        else:
            X_features = X.copy()
        
        self.feature_names = feature_names
        
        # Handle missing values
        X_features = X_features.fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_features)
        
        # Initialize and train Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_scaled)
        self.is_fitted = True
        
        logger.info("Model training completed")
    
    def predict_anomaly_scores(self, X: pd.DataFrame) -> np.ndarray:
        """Predict anomaly scores for new data"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Remove user_id column if present
        if 'user_id' in X.columns:
            X_features = X.drop('user_id', axis=1)
        else:
            X_features = X.copy()
        
        # Handle missing values
        X_features = X_features.fillna(0)
        
        # Scale features
        X_scaled = self.scaler.transform(X_features)
        
        # Get anomaly scores (negative values indicate anomalies)
        anomaly_scores = self.model.decision_function(X_scaled)
        
        # Convert to positive scores where higher values indicate more anomalous behavior
        normalized_scores = (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min())
        inverted_scores = 1 - normalized_scores  # Higher values = more anomalous
        
        return inverted_scores
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict anomalies (-1 for anomaly, 1 for normal)"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Remove user_id column if present
        if 'user_id' in X.columns:
            X_features = X.drop('user_id', axis=1)
        else:
            X_features = X.copy()
        
        # Handle missing values
        X_features = X_features.fillna(0)
        
        # Scale features
        X_scaled = self.scaler.transform(X_features)
        
        return self.model.predict(X_scaled)

class AnomalyDetectionFramework:
    """Main framework that orchestrates the entire anomaly detection process"""
    
    def __init__(self, threshold=0.6, contamination=0.1):
        self.threshold = threshold
        self.contamination = contamination
        self.preprocessor = LogPreprocessor()
        self.feature_extractor = UserFeatureExtractor()
        self.isolation_forest = ExtendedIsolationForest(contamination=contamination)
        self.results = {}
    
    def process_logs(self, log_files: List[str]) -> Dict[str, Any]:
        """Complete pipeline for processing logs and detecting anomalies"""
        logger.info("Starting anomaly detection framework...")
        
        # Step 1: Log Preprocessing
        user_logs = self.preprocessor.preprocess_log_files(log_files)
        
        if not user_logs:
            logger.error("No user logs found after preprocessing")
            return {}
        
        # Step 2: Feature Extraction
        feature_df = self.feature_extractor.extract_all_features(user_logs)
        
        if feature_df.empty:
            logger.error("No features extracted")
            return {}
        
        # Step 3: Train Extended Isolation Forest
        self.isolation_forest.fit(feature_df, self.feature_extractor.feature_names)
        
        # Step 4: Get Anomaly Scores
        anomaly_scores = self.isolation_forest.predict_anomaly_scores(feature_df)
        
        # Step 5: Apply Threshold and Classify
        classifications = self.classify_users(anomaly_scores, feature_df['user_id'].values)
        
        # Store results
        self.results = {
            'user_logs': user_logs,
            'features': feature_df,
            'anomaly_scores': anomaly_scores,
            'classifications': classifications,
            'threshold': self.threshold,
            'normal_users': [user for user, label in classifications.items() if label == 'Normal'],
            'abnormal_users': [user for user, label in classifications.items() if label == 'Abnormal']
        }
        
        logger.info(f"Detection completed: {len(self.results['normal_users'])} normal users, "
                   f"{len(self.results['abnormal_users'])} abnormal users")
        
        return self.results
    
    def classify_users(self, anomaly_scores: np.ndarray, user_ids: np.ndarray) -> Dict[str, str]:
        """Classify users based on anomaly scores and threshold"""
        classifications = {}
        
        for user_id, score in zip(user_ids, anomaly_scores):
            if score > self.threshold:
                classifications[user_id] = 'Abnormal'
            else:
                classifications[user_id] = 'Normal'
        
        return classifications
    
    def get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific user"""
        if user_id not in self.results.get('user_logs', {}):
            return {}
        
        user_logs = self.results['user_logs'][user_id]
        user_features = self.results['features'][self.results['features']['user_id'] == user_id].iloc[0].to_dict()
        user_score = self.results['anomaly_scores'][list(self.results['features']['user_id']).index(user_id)]
        user_classification = self.results['classifications'][user_id]
        
        return {
            'user_id': user_id,
            'total_logs': len(user_logs),
            'anomaly_score': user_score,
            'classification': user_classification,
            'features': user_features,
            'recent_logs': user_logs[-10:] if len(user_logs) > 10 else user_logs
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive report of the anomaly detection results"""
        if not self.results:
            return "No results available. Please run the detection process first."
        
        report = []
        report.append("=" * 60)
        report.append("ANOMALY DETECTION REPORT")
        report.append("=" * 60)
        report.append(f"Threshold: {self.threshold}")
        report.append(f"Total Users Analyzed: {len(self.results['classifications'])}")
        report.append(f"Normal Users: {len(self.results['normal_users'])}")
        report.append(f"Abnormal Users: {len(self.results['abnormal_users'])}")
        report.append(f"Anomaly Rate: {len(self.results['abnormal_users']) / len(self.results['classifications']) * 100:.2f}%")
        report.append("")
        
        # Top anomalous users
        if self.results['abnormal_users']:
            report.append("TOP ANOMALOUS USERS:")
            report.append("-" * 30)
            
            # Sort abnormal users by anomaly score
            abnormal_scores = []
            for user_id in self.results['abnormal_users']:
                idx = list(self.results['features']['user_id']).index(user_id)
                score = self.results['anomaly_scores'][idx]
                abnormal_scores.append((user_id, score))
            
            abnormal_scores.sort(key=lambda x: x[1], reverse=True)
            
            for user_id, score in abnormal_scores[:10]:  # Top 10
                report.append(f"User: {user_id}, Anomaly Score: {score:.4f}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)

# Example usage and demonstration
if __name__ == "__main__":
    # Create framework instance
    framework = AnomalyDetectionFramework(threshold=0.6, contamination=0.1)
    
    # Generate sample log files for demonstration
    print("Generating sample log data...")
    sample_files = framework.preprocessor.create_sample_logs(num_users=50, logs_per_user=100)
    
    # Process logs and detect anomalies
    print("Processing logs and detecting anomalies...")
    results = framework.process_logs(sample_files)
    
    # Generate and display report
    print("\n" + framework.generate_report())
    
    # Show details for a few users
    print("\nDETAILED USER ANALYSIS:")
    print("-" * 40)
    
    # Show normal user example
    if results['normal_users']:
        normal_user = results['normal_users'][0]
        details = framework.get_user_details(normal_user)
        print(f"Normal User Example - {normal_user}:")
        print(f"  Anomaly Score: {details['anomaly_score']:.4f}")
        print(f"  Total Logs: {details['total_logs']}")
        print(f"  Classification: {details['classification']}")
        print()
    
    # Show abnormal user example
    if results['abnormal_users']:
        abnormal_user = results['abnormal_users'][0]
        details = framework.get_user_details(abnormal_user)
        print(f"Abnormal User Example - {abnormal_user}:")
        print(f"  Anomaly Score: {details['anomaly_score']:.4f}")
        print(f"  Total Logs: {details['total_logs']}")
        print(f"  Classification: {details['classification']}")
        print()
    
    print("Framework implementation complete!")