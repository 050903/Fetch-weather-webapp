// Weather Analytics Dashboard JavaScript

class WeatherDashboard {
    constructor() {
        this.apiBase = '/api';
        this.temperatureChart = null;
        this.refreshInterval = null;
        this.socket = null;
        this.init();
    }

    init() {
        this.initializeSocket();
        this.loadDashboardData();
        this.setupEventListeners();
    }

    initializeSocket() {
        // Khởi tạo Socket.IO connection
        this.socket = io();
        
        // Xử lý các sự kiện Socket.IO
        this.socket.on('connect', () => {
            console.log('Đã kết nối WebSocket');
            this.showStatus('Kết nối realtime thành công', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Mất kết nối WebSocket');
            this.showStatus('Mất kết nối realtime', 'error');
        });
        
        this.socket.on('dashboard_update', (data) => {
            console.log('Nhận cập nhật dashboard:', data);
            this.updateStatistics(data.statistics);
            this.updateCurrentWeather(data.cities_data);
        });
        
        this.socket.on('latest_data_update', (data) => {
            console.log('Nhận dữ liệu mới nhất:', data);
            this.updateDataTable(data.data);
            this.updateTemperatureChart(data.data);
        });
        
        this.socket.on('new_weather_data', (data) => {
            console.log('Nhận dữ liệu thời tiết mới:', data);
            this.showStatus(`Dữ liệu mới từ ${data.data.city}`, 'info');
            // Tự động làm mới sau khi có dữ liệu mới
            setTimeout(() => {
                this.requestLatestData();
            }, 1000);
        });
        
        this.socket.on('status_update', (data) => {
            console.log('Nhận cập nhật trạng thái:', data);
            this.showStatus(data.message, data.type);
        });
        
        this.socket.on('time_update', (data) => {
            // Cập nhật thời gian thực
            this.updateCurrentTime(data.current_time);
        });
    }

    requestLatestData() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('request_data', { type: 'latest' });
        }
    }

    requestDashboardData() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('request_data', { type: 'dashboard' });
        }
    }

    setupEventListeners() {
        // Cập nhật thời gian hiện tại mỗi giây
        setInterval(() => {
            this.updateCurrentTime();
        }, 1000);
        
        // Sử dụng WebSocket thay vì polling, chỉ giữ fallback
        this.refreshInterval = setInterval(() => {
            if (!this.socket || !this.socket.connected) {
                this.loadDashboardData();
            }
        }, 60000); // 1 phút cho fallback
    }

    setupAutoRefresh() {
        // Không cần auto refresh nữa vì đã có WebSocket realtime
        console.log('WebSocket realtime đã được kích hoạt');
    }

    async loadDashboardData() {
        try {
            this.showStatus('Đang tải dữ liệu dashboard...', 'info');
            
            const response = await fetch(`${this.apiBase}/weather/dashboard`);
            const data = await response.json();
            
            if (data.success) {
                this.updateStatistics(data.statistics);
                this.updateCurrentWeather(data.cities_data);
                this.loadLatestData();
                this.showStatus('Dữ liệu đã được cập nhật', 'success');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Lỗi tải dashboard:', error);
            this.showStatus('Lỗi tải dữ liệu dashboard', 'error');
        }
    }

    async loadLatestData() {
        try {
            const response = await fetch(`${this.apiBase}/weather/latest?limit=20`);
            const data = await response.json();
            
            if (data.success) {
                this.updateDataTable(data.data);
                this.updateTemperatureChart(data.data);
            }
        } catch (error) {
            console.error('Lỗi tải dữ liệu mới nhất:', error);
        }
    }

    updateStatistics(stats) {
        document.getElementById('totalRecords').textContent = stats.total_records || 0;
        document.getElementById('citiesCount').textContent = stats.cities_count || 0;
        
        if (stats.last_updated) {
            const lastUpdated = new Date(stats.last_updated);
            document.getElementById('lastUpdated').textContent = 
                lastUpdated.toLocaleTimeString('vi-VN', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
        }
    }

    updateCurrentWeather(citiesData) {
        const container = document.getElementById('currentWeather');
        
        if (!citiesData || Object.keys(citiesData).length === 0) {
            container.innerHTML = '<div class="loading">Không có dữ liệu thời tiết</div>';
            return;
        }

        let totalTemp = 0;
        let count = 0;
        
        const weatherHTML = Object.values(citiesData).map(weather => {
            totalTemp += weather.temperature;
            count++;
            
            return `
                <div class="weather-item">
                    <div class="city">${weather.city}</div>
                    <div class="temp">${weather.temperature}°C</div>
                    <div class="desc">${weather.weather_description}</div>
                    <div style="font-size: 0.8rem; margin-top: 5px;">
                        Độ ẩm: ${weather.humidity}% | Gió: ${weather.wind_speed} m/s
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = weatherHTML;

        // Cập nhật nhiệt độ trung bình
        if (count > 0) {
            const avgTemp = (totalTemp / count).toFixed(1);
            document.getElementById('avgTemp').textContent = `${avgTemp}°C`;
        }
    }

    updateDataTable(data) {
        const tbody = document.querySelector('#dataTable tbody');
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="loading">Không có dữ liệu</td></tr>';
            return;
        }

        const tableHTML = data.map(record => {
            const timestamp = new Date(record.timestamp);
            return `
                <tr>
                    <td>${timestamp.toLocaleString('vi-VN')}</td>
                    <td>${record.city}</td>
                    <td>${record.temperature}°C</td>
                    <td>${record.feels_like}°C</td>
                    <td>${record.humidity}%</td>
                    <td>${record.pressure} hPa</td>
                    <td>${record.wind_speed} m/s</td>
                    <td>${record.weather_description}</td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = tableHTML;
    }

    updateTemperatureChart(data) {
        const ctx = document.getElementById('temperatureChart').getContext('2d');
        
        if (this.temperatureChart) {
            this.temperatureChart.destroy();
        }

        if (!data || data.length === 0) {
            return;
        }

        // Nhóm dữ liệu theo thành phố
        const cityData = {};
        data.forEach(record => {
            if (!cityData[record.city]) {
                cityData[record.city] = {
                    labels: [],
                    temperatures: []
                };
            }
            
            const time = new Date(record.timestamp).toLocaleTimeString('vi-VN', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            cityData[record.city].labels.unshift(time);
            cityData[record.city].temperatures.unshift(record.temperature);
        });

        // Tạo datasets cho chart
        const colors = [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)',
            'rgb(75, 192, 192)',
            'rgb(153, 102, 255)'
        ];

        const datasets = Object.keys(cityData).map((city, index) => ({
            label: city,
            data: cityData[city].temperatures.slice(0, 10), // Chỉ lấy 10 điểm gần nhất
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length] + '20',
            tension: 0.4,
            fill: false
        }));

        // Sử dụng labels từ thành phố đầu tiên
        const labels = Object.values(cityData)[0]?.labels.slice(0, 10).reverse() || [];

        this.temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Biến động nhiệt độ theo thời gian'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Nhiệt độ (°C)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Thời gian'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    showStatus(message, type = 'info') {
        const statusEl = document.getElementById('status');
        statusEl.textContent = message;
        statusEl.className = `status ${type}`;
        statusEl.style.display = 'block';

        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 3000);
    }

    async collectWeatherData() {
        try {
            this.showStatus('Đang thu thập dữ liệu thời tiết...', 'info');
            
            const response = await fetch(`${this.apiBase}/weather/collect`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showStatus(data.message, 'success');
                // Refresh dashboard after collecting data
                setTimeout(() => {
                    this.loadDashboardData();
                }, 1000);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Lỗi thu thập dữ liệu:', error);
            this.showStatus('Lỗi thu thập dữ liệu thời tiết', 'error');
        }
    }

    updateCurrentTime(isoTime = null) {
        const now = isoTime ? new Date(isoTime) : new Date();
        const timeString = now.toLocaleTimeString('vi-VN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        const currentTimeEl = document.getElementById('currentTime');
        if (currentTimeEl) {
            currentTimeEl.textContent = timeString;
        }
    }

    refreshDashboard() {
        this.showStatus('Đang làm mới dashboard...', 'info');
        
        // Ưu tiên sử dụng WebSocket nếu có kết nối
        if (this.socket && this.socket.connected) {
            this.requestDashboardData();
            this.requestLatestData();
        } else {
            // Fallback về HTTP API
            this.loadDashboardData();
        }
    }

    async exportData() {
        try {
            this.showStatus('Đang xuất báo cáo...', 'info');
            
            const response = await fetch(`${this.apiBase}/weather/latest?limit=100`);
            const data = await response.json();
            
            if (data.success) {
                this.downloadCSV(data.data);
                this.showStatus('Báo cáo đã được tải xuống', 'success');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Lỗi xuất báo cáo:', error);
            this.showStatus('Lỗi xuất báo cáo', 'error');
        }
    }

    downloadCSV(data) {
        const headers = [
            'Thời gian',
            'Thành phố',
            'Quốc gia',
            'Nhiệt độ (°C)',
            'Cảm giác như (°C)',
            'Độ ẩm (%)',
            'Áp suất (hPa)',
            'Tốc độ gió (m/s)',
            'Hướng gió (°)',
            'Thời tiết',
            'Mô tả',
            'Tầm nhìn (m)',
            'Chỉ số UV'
        ];

        const csvContent = [
            headers.join(','),
            ...data.map(record => [
                new Date(record.timestamp).toLocaleString('vi-VN'),
                record.city,
                record.country,
                record.temperature,
                record.feels_like,
                record.humidity,
                record.pressure,
                record.wind_speed,
                record.wind_direction,
                record.weather_main,
                record.weather_description,
                record.visibility || '',
                record.uv_index || ''
            ].join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `weather_report_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Global functions for button clicks
function collectWeatherData() {
    dashboard.collectWeatherData();
}

function refreshDashboard() {
    dashboard.refreshDashboard();
}

function exportData() {
    dashboard.exportData();
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new WeatherDashboard();
});

