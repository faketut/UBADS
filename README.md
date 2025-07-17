# UBADS: User Behavior Anomaly Detection System    

A comprehensive web-based system for detecting anomalous user behavior patterns in log files using machine learning techniques.

[![](https://i9.ytimg.com/vi_webp/5LkUzYP4coQ/mq2.webp?sqp=CJDY5MMG-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGGUgZShlMA8=&rs=AOn4CLBmjSzkmNNwFaYDMlFJS8W4L3dlng)](https://www.youtube.com/watch?v=5LkUzYP4coQ&feature=youtu.be)


## Features

- **Web-based Interface**: Modern, responsive UI built with Flask and Bootstrap
- **Log Processing**: Automatic parsing and preprocessing of log files
- **Feature Extraction**: Advanced feature engineering for user behavior analysis
- **Anomaly Detection**: Isolation Forest algorithm for detecting unusual patterns
- **Real-time Analysis**: Interactive dashboard with charts and visualizations
- **Sample Data Generation**: Built-in sample data generator for testing
- **Report Generation**: Detailed analysis reports with downloadable formats
- **Configuration Management**: Flexible configuration system

## System Architecture

```
├── main.py              # Core anomaly detection logic
├── app.py               # Flask web application
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
│   └── index.html      # Main dashboard template
├── static/             # Static assets
│   ├── css/
│   │   └── style.css   # Custom styles
│   ├── js/
│   │   └── app.js      # Frontend JavaScript
│   └── images/         # Image assets
└── uploads/            # Uploaded log files
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd User-Behavior-Anomaly-Detection-System
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5000`

## Usage Guide

### 1. Dashboard Overview

The dashboard provides a comprehensive overview of the anomaly detection results:
- **Status Cards**: Display counts of normal/abnormal users and anomaly rates
- **Charts**: Visual representation of user distribution and anomaly scores
- **Real-time Updates**: Live updates as analysis progresses

### 2. File Upload

1. Navigate to the **Analysis** section
2. Click **Choose Files** to select log files
3. Supported formats: `.txt`, `.log`, `.csv`
4. Click **Upload Files** to process

### 3. Sample Data Generation

For testing purposes, you can generate sample log data:
1. Set the number of users and logs per user
2. Click **Generate Sample Data**
3. The system will create realistic log patterns with embedded anomalies

### 4. Analysis Configuration

Adjust analysis parameters:
- **Anomaly Threshold**: Controls sensitivity (0.0 - 1.0)
- **Contamination**: Expected proportion of anomalies (0.01 - 0.5)

### 5. Results Interpretation

- **Normal Users**: Users with typical behavior patterns
- **Abnormal Users**: Users exhibiting unusual behavior
- **Anomaly Scores**: Higher scores indicate more anomalous behavior
- **User Details**: Click "Details" for comprehensive user analysis

## Configuration

The system uses a centralized configuration system (`config.py`):

### Key Configuration Sections

- **Flask Settings**: Server configuration
- **Upload Settings**: File upload limits and allowed formats
- **Anomaly Detection**: Algorithm parameters
- **Feature Extraction**: Feature engineering options
- **UI Settings**: Interface customization

### Environment Variables

```bash
# Server Configuration
export SECRET_KEY="your-secret-key"
export DEBUG="True"
export HOST="0.0.0.0"
export PORT="5000"

# Database (optional)
export DATABASE_URL="sqlite:///anomaly_detection.db"

# Notifications (optional)
export WEBHOOK_URL="https://your-webhook-url.com"
```

## Log Format

The system expects log files with the following format:

```
2024-01-15 10:30:45 user:user123 192.168.1.100 GET /api/data status:200 time:150ms
2024-01-15 10:31:02 user:user123 192.168.1.100 POST /login status:200 time:300ms
2024-01-15 10:32:15 user:user456 192.168.1.101 GET /admin status:403 time:500ms
```

### Supported Log Fields

- **Timestamp**: ISO format datetime
- **User ID**: User identifier
- **IP Address**: Client IP address
- **Action**: HTTP method or action type
- **Resource**: Requested resource path
- **Status Code**: HTTP response status
- **Response Time**: Request processing time

## API Endpoints

### Core Endpoints

- `GET /` - Main dashboard
- `POST /api/upload` - File upload
- `POST /api/analyze` - Start analysis
- `GET /api/results` - Get analysis results
- `GET /api/user/<user_id>` - User details
- `GET /api/report` - Generate report
- `GET /api/download-report` - Download report
- `GET /api/config` - Get configuration
- `PUT /api/config` - Update configuration

### Health Check

- `GET /api/health` - System health status

## Features Extracted

The system extracts various features from user behavior:

### Time-based Features
- Total logs per user
- Unique days of activity
- Night activity ratio
- Weekend activity ratio

### Action-based Features
- Failed login ratio
- Delete action ratio
- Admin action ratio
- Unique actions count

### Resource-based Features
- Unique resources accessed
- Admin access ratio
- Resource diversity

### Status-based Features
- Error rate
- Success rate
- Unique status codes

### Performance Features
- Average response time
- Maximum response time
- Response time standard deviation
- Slow requests ratio

## Algorithm Details

### Isolation Forest

The system uses the Isolation Forest algorithm for anomaly detection:

- **Principle**: Anomalies are easier to isolate than normal points
- **Advantages**: Fast, scalable, handles high-dimensional data
- **Parameters**: Contamination rate, number of estimators
- **Output**: Anomaly scores and binary classifications

### Feature Engineering

1. **Log Parsing**: Extract structured data from raw logs
2. **User Grouping**: Organize logs by user ID
3. **Feature Calculation**: Compute behavioral metrics
4. **Normalization**: Scale features for algorithm compatibility

## Troubleshooting

### Common Issues

1. **File Upload Errors**
   - Check file format (must be .txt, .log, or .csv)
   - Ensure file size is under 16MB
   - Verify file permissions

2. **Analysis Failures**
   - Check log format compatibility
   - Ensure sufficient data for analysis
   - Verify Python dependencies are installed

3. **Performance Issues**
   - Reduce number of users/logs for testing
   - Adjust contamination parameter
   - Check system resources

### Debug Mode

Enable debug mode for detailed error information:

```bash
export DEBUG="True"
python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration documentation

## Version History

- **v1.0.0**: Initial release with core functionality
- Web-based interface
- Isolation Forest algorithm
- Feature extraction pipeline
- Report generation
- Configuration management 
