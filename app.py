from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("Warning: Flask-CORS not available. CORS support disabled.")
import os
import json
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback
import logging
from typing import Dict, List, Any

from config import Config
from main import AnomalyDetectionFramework, LogPreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS if available
if CORS_AVAILABLE:
    CORS(app)

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Global variables to store current analysis results
current_results = {}
current_framework = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', config=Config.get_all_config())

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload for log analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'filepath': filepath
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_logs():
    """Analyze uploaded log files"""
    global current_results, current_framework
    
    try:
        data = request.get_json()
        files = data.get('files', [])
        threshold = data.get('threshold', Config.DEFAULT_THRESHOLD)
        contamination = data.get('contamination', Config.DEFAULT_CONTAMINATION)
        
        if not files:
            return jsonify({'error': 'No files provided for analysis'}), 400
        
        # Create file paths
        file_paths = [os.path.join(Config.UPLOAD_FOLDER, f) for f in files]
        
        # Initialize framework
        current_framework = AnomalyDetectionFramework(
            threshold=threshold,
            contamination=contamination
        )
        
        # Process logs
        current_results = current_framework.process_logs(file_paths)
        
        if not current_results:
            return jsonify({'error': 'No results generated'}), 500
        
        # Prepare response data
        response_data = {
            'total_users': len(current_results['classifications']),
            'normal_users': len(current_results['normal_users']),
            'abnormal_users': len(current_results['abnormal_users']),
            'anomaly_rate': len(current_results['abnormal_users']) / len(current_results['classifications']) * 100,
            'threshold': threshold,
            'contamination': contamination,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/generate-sample', methods=['POST'])
def generate_sample_data():
    """Generate sample log data"""
    try:
        data = request.get_json()
        num_users = data.get('num_users', Config.DEFAULT_NUM_USERS)
        logs_per_user = data.get('logs_per_user', Config.DEFAULT_LOGS_PER_USER)
        
        preprocessor = LogPreprocessor()
        sample_files = preprocessor.create_sample_logs(
            num_users=num_users,
            logs_per_user=logs_per_user
        )
        
        return jsonify({
            'message': 'Sample data generated successfully',
            'files': sample_files,
            'num_users': num_users,
            'logs_per_user': logs_per_user
        })
        
    except Exception as e:
        logger.error(f"Sample generation error: {str(e)}")
        return jsonify({'error': f'Sample generation failed: {str(e)}'}), 500

@app.route('/api/results')
def get_results():
    """Get current analysis results"""
    global current_results
    
    if not current_results:
        return jsonify({'error': 'No results available'}), 404
    
    try:
        # Prepare detailed results
        results_data = {
            'summary': {
                'total_users': len(current_results['classifications']),
                'normal_users': len(current_results['normal_users']),
                'abnormal_users': len(current_results['abnormal_users']),
                'anomaly_rate': len(current_results['abnormal_users']) / len(current_results['classifications']) * 100
            },
            'users': []
        }
        
        # Add user details
        for user_id in current_results['classifications']:
            user_details = current_framework.get_user_details(user_id)
            results_data['users'].append(user_details)
        
        return jsonify(results_data)
        
    except Exception as e:
        logger.error(f"Results retrieval error: {str(e)}")
        return jsonify({'error': f'Failed to retrieve results: {str(e)}'}), 500

@app.route('/api/user/<user_id>')
def get_user_details(user_id):
    """Get detailed information about a specific user"""
    global current_framework
    
    if not current_framework:
        return jsonify({'error': 'No analysis performed yet'}), 404
    
    try:
        user_details = current_framework.get_user_details(user_id)
        if not user_details:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user_details)
        
    except Exception as e:
        logger.error(f"User details error: {str(e)}")
        return jsonify({'error': f'Failed to get user details: {str(e)}'}), 500

@app.route('/api/config', methods=['GET', 'PUT'])
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify(Config.get_all_config())
    
    elif request.method == 'PUT':
        try:
            config_updates = request.get_json()
            Config.update_config(config_updates)
            return jsonify({'message': 'Configuration updated successfully'})
        except Exception as e:
            logger.error(f"Config update error: {str(e)}")
            return jsonify({'error': f'Configuration update failed: {str(e)}'}), 500

@app.route('/api/report')
def generate_report():
    """Generate and return analysis report"""
    global current_framework
    
    if not current_framework:
        return jsonify({'error': 'No analysis performed yet'}), 404
    
    try:
        report = current_framework.generate_report()
        return jsonify({'report': report})
        
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@app.route('/api/download-report')
def download_report():
    """Download analysis report as text file"""
    global current_framework
    
    if not current_framework:
        return jsonify({'error': 'No analysis performed yet'}), 404
    
    try:
        report = current_framework.generate_report()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(report)
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'anomaly_detection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        )
        
    except Exception as e:
        logger.error(f"Report download error: {str(e)}")
        return jsonify({'error': f'Report download failed: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'cors_enabled': CORS_AVAILABLE
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 