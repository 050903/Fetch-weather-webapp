# Weather Analytics Dashboard - Hướng dẫn sử dụng

## Tổng quan

Weather Analytics Dashboard là một ứng dụng web Python được xây dựng để thu thập, phân tích và hiển thị dữ liệu thời tiết theo thời gian thực. Ứng dụng cung cấp bảng điều khiển trực quan với biểu đồ và báo cáo chi tiết.

## Tính năng chính

### 1. Thu thập dữ liệu thời tiết tự động
- Thu thập dữ liệu từ 5 thành phố lớn của Việt Nam: TP.HCM, Hà Nội, Đà Nẵng, Cần Thơ, Huế
- Cập nhật dữ liệu tự động mỗi 10 phút
- Lưu trữ dữ liệu vào cơ sở dữ liệu SQLite

### 2. Bảng điều khiển trực quan
- Hiển thị thống kê tổng quan: tổng số bản ghi, số thành phố, thời gian cập nhật cuối, nhiệt độ trung bình
- Thẻ thời tiết hiện tại cho từng thành phố với thông tin chi tiết
- Biểu đồ nhiệt độ theo thời gian với nhiều đường biểu diễn cho các thành phố

### 3. Cập nhật thời gian thực
- Sử dụng WebSocket (Socket.IO) để cập nhật dữ liệu tự động
- Không cần làm mới trang để xem dữ liệu mới nhất
- Thông báo trạng thái realtime

### 4. Bảng dữ liệu chi tiết
- Hiển thị dữ liệu thời tiết chi tiết trong bảng
- Bao gồm: thời gian, thành phố, nhiệt độ, cảm giác như, độ ẩm, áp suất, tốc độ gió, mô tả thời tiết

### 5. Xuất báo cáo
- Xuất dữ liệu thành file CSV
- Bao gồm 100 bản ghi gần nhất
- Tải xuống trực tiếp từ trình duyệt

## Cách sử dụng

### Truy cập ứng dụng
- URL công khai: https://qjh9iecejo98.manus.space
- Ứng dụng tương thích với cả desktop và mobile

### Các chức năng chính

#### 1. Thu thập dữ liệu thủ công
- Click nút "Thu thập dữ liệu" để thu thập dữ liệu mới cho tất cả thành phố
- Dữ liệu sẽ được cập nhật ngay lập tức trên dashboard

#### 2. Làm mới dashboard
- Click nút "Làm mới" để cập nhật toàn bộ dashboard
- Hữu ích khi kết nối WebSocket bị gián đoạn

#### 3. Xuất báo cáo
- Click nút "Xuất báo cáo" để tải file CSV chứa dữ liệu
- File sẽ được đặt tên theo định dạng: weather_report_YYYY-MM-DD.csv

## Kiến trúc kỹ thuật

### Backend (Flask)
- **Framework**: Flask với Flask-SocketIO
- **Database**: SQLite với SQLAlchemy ORM
- **API**: RESTful API endpoints
- **Realtime**: WebSocket với Socket.IO
- **Background Tasks**: Threading cho thu thập dữ liệu tự động

### Frontend
- **Technology**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js cho biểu đồ
- **Realtime**: Socket.IO client
- **Responsive**: Mobile-friendly design

### Cơ sở dữ liệu
- **Model**: WeatherData với các trường:
  - id, city, country, temperature, feels_like
  - humidity, pressure, wind_speed, wind_direction
  - weather_main, weather_description, visibility, uv_index, timestamp

## API Endpoints

### Weather API
- `GET /api/weather/current?city=<city_name>` - Lấy dữ liệu thời tiết hiện tại
- `GET /api/weather/latest?limit=<number>` - Lấy dữ liệu mới nhất
- `GET /api/weather/city/<city_name>?limit=<number>` - Lấy dữ liệu theo thành phố
- `GET /api/weather/dashboard` - Lấy dữ liệu dashboard
- `POST /api/weather/collect` - Thu thập dữ liệu cho tất cả thành phố

### WebSocket Events
- `connect` - Kết nối client
- `disconnect` - Ngắt kết nối client
- `request_data` - Yêu cầu dữ liệu từ client
- `dashboard_update` - Cập nhật dashboard
- `latest_data_update` - Cập nhật dữ liệu mới nhất
- `new_weather_data` - Dữ liệu thời tiết mới
- `status_update` - Cập nhật trạng thái

## Cấu trúc thư mục

```
weather-analytics/
├── src/
│   ├── models/
│   │   ├── user.py          # User model (template)
│   │   └── weather.py       # Weather data model
│   ├── routes/
│   │   ├── user.py          # User routes (template)
│   │   └── weather.py       # Weather API routes
│   ├── services/
│   │   ├── weather_service.py    # Weather data service
│   │   └── realtime_service.py   # WebSocket service
│   ├── static/
│   │   ├── index.html       # Frontend HTML
│   │   └── app.js          # Frontend JavaScript
│   ├── database/
│   │   └── app.db          # SQLite database
│   └── main.py             # Main application entry point
├── venv/                   # Virtual environment
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Cài đặt và chạy local

### Yêu cầu hệ thống
- Python 3.11+
- pip package manager

### Cài đặt
```bash
# Clone project
cd weather-analytics

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python src/main.py
```

### Truy cập
- Local URL: http://localhost:5002
- Ứng dụng sẽ tự động tạo database và bắt đầu thu thập dữ liệu

## Tính năng nâng cao

### 1. Dữ liệu mẫu (Demo Mode)
- Khi không có API key thực, ứng dụng sử dụng dữ liệu mẫu
- Dữ liệu được tạo ngẫu nhiên nhưng thực tế cho các thành phố Việt Nam

### 2. Background Data Collection
- Thu thập dữ liệu tự động mỗi 10 phút
- Chạy trong background thread
- Tự động phát sóng dữ liệu mới qua WebSocket

### 3. Error Handling
- Xử lý lỗi kết nối API
- Fallback về dữ liệu mẫu khi có lỗi
- Thông báo lỗi realtime cho người dùng

### 4. Performance Optimization
- Lazy loading cho dữ liệu lớn
- Caching dữ liệu dashboard
- Efficient database queries với SQLAlchemy

## Troubleshooting

### Vấn đề thường gặp

1. **Không có dữ liệu hiển thị**
   - Click nút "Thu thập dữ liệu" để khởi tạo dữ liệu
   - Kiểm tra kết nối internet
   - Làm mới trang

2. **WebSocket không kết nối**
   - Kiểm tra firewall/proxy settings
   - Sử dụng chức năng "Làm mới" thay thế
   - Reload trang web

3. **Biểu đồ không hiển thị**
   - Đảm bảo JavaScript được bật
   - Kiểm tra console browser để xem lỗi
   - Thử trình duyệt khác

## Liên hệ và hỗ trợ

Ứng dụng được phát triển bởi Manus AI Assistant. Để được hỗ trợ hoặc báo cáo lỗi, vui lòng liên hệ qua platform Manus.

---

**Phiên bản**: 1.0.0  
**Ngày cập nhật**: 20/06/2025  
**Tác giả**: Manus AI Assistant

