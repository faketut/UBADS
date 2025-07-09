// Main JavaScript for Anomaly Detection System

class AnomalyDetectionApp {
    constructor() {
        this.uploadedFiles = [];
        this.currentResults = null;
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadConfiguration();
        this.initializeCharts();
        this.setupRangeSliders();
    }

    setupEventListeners() {
        // File upload
        document.getElementById('upload-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFileUpload();
        });

        // Sample data generation
        document.getElementById('sample-data-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateSampleData();
        });

        // Analysis form
        document.getElementById('analysis-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startAnalysis();
        });

        // Download report
        document.getElementById('download-report-btn').addEventListener('click', () => {
            this.downloadReport();
        });

        // Refresh results
        document.getElementById('refresh-results-btn').addEventListener('click', () => {
            this.loadResults();
        });

        // Range sliders
        document.getElementById('threshold').addEventListener('input', (e) => {
            document.getElementById('threshold-value').textContent = e.target.value;
        });

        document.getElementById('contamination').addEventListener('input', (e) => {
            document.getElementById('contamination-value').textContent = e.target.value;
        });

        // File input change
        document.getElementById('log-files').addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files);
        });
    }

    setupRangeSliders() {
        // Initialize range slider values
        const thresholdSlider = document.getElementById('threshold');
        const contaminationSlider = document.getElementById('contamination');
        
        document.getElementById('threshold-value').textContent = thresholdSlider.value;
        document.getElementById('contamination-value').textContent = contaminationSlider.value;
    }

    async loadConfiguration() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            this.displayConfiguration(config);
        } catch (error) {
            console.error('Failed to load configuration:', error);
            this.showAlert('Failed to load configuration', 'danger');
        }
    }

    displayConfiguration(config) {
        const configContent = document.getElementById('config-content');
        let html = '';

        for (const [section, settings] of Object.entries(config)) {
            html += `
                <div class="config-section">
                    <h6><i class="fas fa-cog me-2"></i>${this.capitalizeFirst(section)}</h6>
                    <div class="row">
            `;

            for (const [key, value] of Object.entries(settings)) {
                const displayValue = typeof value === 'object' ? JSON.stringify(value) : value;
                html += `
                    <div class="col-md-6 mb-2">
                        <small class="text-muted">${key}:</small>
                        <div class="fw-bold">${displayValue}</div>
                    </div>
                `;
            }

            html += `
                    </div>
                </div>
            `;
        }

        configContent.innerHTML = html;
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    handleFileSelection(files) {
        this.uploadedFiles = Array.from(files);
        const analyzeBtn = document.getElementById('analyze-btn');
        analyzeBtn.disabled = this.uploadedFiles.length === 0;
        
        if (this.uploadedFiles.length > 0) {
            this.showAlert(`Selected ${this.uploadedFiles.length} file(s)`, 'info');
        }
    }

    async handleFileUpload() {
        const fileInput = document.getElementById('log-files');
        const files = fileInput.files;

        if (files.length === 0) {
            this.showAlert('Please select files to upload', 'warning');
            return;
        }

        this.showLoading('Uploading files...');

        try {
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || 'Upload failed');
                }
            }

            this.hideLoading();
            this.showAlert('Files uploaded successfully!', 'success');
            this.uploadedFiles = Array.from(files);
            document.getElementById('analyze-btn').disabled = false;

        } catch (error) {
            this.hideLoading();
            this.showAlert(`Upload failed: ${error.message}`, 'danger');
        }
    }

    async generateSampleData() {
        const numUsers = document.getElementById('num-users').value;
        const logsPerUser = document.getElementById('logs-per-user').value;

        this.showLoading('Generating sample data...');

        try {
            const response = await fetch('/api/generate-sample', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    num_users: parseInt(numUsers),
                    logs_per_user: parseInt(logsPerUser)
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Sample generation failed');
            }

            this.hideLoading();
            this.showAlert('Sample data generated successfully!', 'success');
            
            // Auto-fill the uploaded files
            this.uploadedFiles = result.files;
            document.getElementById('analyze-btn').disabled = false;

        } catch (error) {
            this.hideLoading();
            this.showAlert(`Sample generation failed: ${error.message}`, 'danger');
        }
    }

    async startAnalysis() {
        if (this.uploadedFiles.length === 0) {
            this.showAlert('Please upload files or generate sample data first', 'warning');
            return;
        }

        const threshold = parseFloat(document.getElementById('threshold').value);
        const contamination = parseFloat(document.getElementById('contamination').value);

        this.showLoading('Analyzing logs... This may take a few moments.');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    files: this.uploadedFiles.map(f => f.name || f),
                    threshold: threshold,
                    contamination: contamination
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Analysis failed');
            }

            this.hideLoading();
            this.showAlert('Analysis completed successfully!', 'success');
            
            // Update dashboard
            this.updateDashboard(result);
            
            // Load detailed results
            await this.loadResults();

        } catch (error) {
            this.hideLoading();
            this.showAlert(`Analysis failed: ${error.message}`, 'danger');
        }
    }

    updateDashboard(data) {
        document.getElementById('normal-users-count').textContent = data.normal_users;
        document.getElementById('abnormal-users-count').textContent = data.abnormal_users;
        document.getElementById('total-users-count').textContent = data.total_users;
        document.getElementById('anomaly-rate').textContent = `${data.anomaly_rate.toFixed(1)}%`;

        // Update charts
        this.updateCharts(data);
    }

    async loadResults() {
        try {
            const response = await fetch('/api/results');
            const results = await response.json();

            if (!response.ok) {
                throw new Error(results.error || 'Failed to load results');
            }

            this.currentResults = results;
            this.displayResults(results);

        } catch (error) {
            this.showAlert(`Failed to load results: ${error.message}`, 'danger');
        }
    }

    displayResults(results) {
        const tbody = document.getElementById('results-tbody');
        
        if (!results.users || results.users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        No results available. Please run an analysis first.
                    </td>
                </tr>
            `;
            return;
        }

        let html = '';
        
        results.users.forEach(user => {
            const badgeClass = user.classification === 'Normal' ? 'badge-normal' : 'badge-abnormal';
            const rowClass = user.classification === 'Abnormal' ? 'table-danger' : '';
            
            html += `
                <tr class="${rowClass}">
                    <td><strong>${user.user_id}</strong></td>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="progress me-2" style="width: 100px;">
                                <div class="progress-bar ${user.classification === 'Abnormal' ? 'bg-danger' : 'bg-success'}" 
                                     style="width: ${(user.anomaly_score * 100).toFixed(1)}%"></div>
                            </div>
                            <small>${user.anomaly_score.toFixed(3)}</small>
                        </div>
                    </td>
                    <td><span class="badge ${badgeClass}">${user.classification}</span></td>
                    <td>${user.total_logs}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="app.showUserDetails('${user.user_id}')">
                            <i class="fas fa-eye me-1"></i>Details
                        </button>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = html;
    }

    async showUserDetails(userId) {
        try {
            const response = await fetch(`/api/user/${userId}`);
            const userDetails = await response.json();

            if (!response.ok) {
                throw new Error(userDetails.error || 'Failed to load user details');
            }

            this.displayUserDetailsModal(userDetails);

        } catch (error) {
            this.showAlert(`Failed to load user details: ${error.message}`, 'danger');
        }
    }

    displayUserDetailsModal(userDetails) {
        const modalContent = document.getElementById('user-details-content');
        
        let html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>User Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>User ID:</strong></td><td>${userDetails.user_id}</td></tr>
                        <tr><td><strong>Classification:</strong></td><td>
                            <span class="badge ${userDetails.classification === 'Normal' ? 'badge-normal' : 'badge-abnormal'}">
                                ${userDetails.classification}
                            </span>
                        </td></tr>
                        <tr><td><strong>Anomaly Score:</strong></td><td>${userDetails.anomaly_score.toFixed(4)}</td></tr>
                        <tr><td><strong>Total Logs:</strong></td><td>${userDetails.total_logs}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Key Features</h6>
                    <div class="row">
        `;

        // Display key features
        const features = userDetails.features || {};
        const keyFeatures = ['failed_login_ratio', 'error_rate', 'night_activity_ratio', 'admin_access_ratio'];
        
        keyFeatures.forEach(feature => {
            if (features[feature] !== undefined) {
                const value = typeof features[feature] === 'number' ? features[feature].toFixed(3) : features[feature];
                html += `
                    <div class="col-6 mb-2">
                        <small class="text-muted">${feature.replace(/_/g, ' ').toUpperCase()}:</small>
                        <div class="fw-bold">${value}</div>
                    </div>
                `;
            }
        });

        html += `
                    </div>
                </div>
            </div>
        `;

        // Recent logs
        if (userDetails.recent_logs && userDetails.recent_logs.length > 0) {
            html += `
                <div class="mt-3">
                    <h6>Recent Logs (Last 10)</h6>
                    <div class="table-responsive" style="max-height: 200px; overflow-y: auto;">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Action</th>
                                    <th>Resource</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            userDetails.recent_logs.forEach(log => {
                html += `
                    <tr>
                        <td><small>${log.timestamp || 'N/A'}</small></td>
                        <td><span class="badge bg-secondary">${log.action || 'N/A'}</span></td>
                        <td><small>${log.resource || 'N/A'}</small></td>
                        <td><span class="badge ${log.status_code >= 400 ? 'bg-danger' : 'bg-success'}">${log.status_code || 'N/A'}</span></td>
                    </tr>
                `;
            });

            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        modalContent.innerHTML = html;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('userDetailsModal'));
        modal.show();
    }

    async downloadReport() {
        try {
            const response = await fetch('/api/download-report');
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Download failed');
            }

            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `anomaly_detection_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showAlert('Report downloaded successfully!', 'success');

        } catch (error) {
            this.showAlert(`Download failed: ${error.message}`, 'danger');
        }
    }

    initializeCharts() {
        // User Distribution Chart
        const userDistributionCtx = document.getElementById('userDistributionChart').getContext('2d');
        this.charts.userDistribution = new Chart(userDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Normal Users', 'Abnormal Users'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: ['#198754', '#dc3545'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Anomaly Scores Chart
        const anomalyScoresCtx = document.getElementById('anomalyScoresChart').getContext('2d');
        this.charts.anomalyScores = new Chart(anomalyScoresCtx, {
            type: 'bar',
            data: {
                labels: ['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'],
                datasets: [{
                    label: 'Number of Users',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: '#0d6efd',
                    borderColor: '#0d6efd',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    updateCharts(data) {
        // Update user distribution chart
        this.charts.userDistribution.data.datasets[0].data = [data.normal_users, data.abnormal_users];
        this.charts.userDistribution.update();

        // Update anomaly scores chart if we have detailed results
        if (this.currentResults && this.currentResults.users) {
            const scores = this.currentResults.users.map(u => u.anomaly_score);
            const bins = [0, 0, 0, 0, 0];
            
            scores.forEach(score => {
                if (score < 0.2) bins[0]++;
                else if (score < 0.4) bins[1]++;
                else if (score < 0.6) bins[2]++;
                else if (score < 0.8) bins[3]++;
                else bins[4]++;
            });

            this.charts.anomalyScores.data.datasets[0].data = bins;
            this.charts.anomalyScores.update();
        }
    }

    showLoading(message = 'Processing...') {
        document.getElementById('loading-message').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }

    hideLoading() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) {
            modal.hide();
        }
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the container
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AnomalyDetectionApp();
});

// Global utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatPercentage(num) {
    return `${(num * 100).toFixed(1)}%`;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
} 