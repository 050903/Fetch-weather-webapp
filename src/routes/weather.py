from flask import Blueprint, jsonify, request
from src.services.weather_service import WeatherService
from src.models.weather import WeatherData, db
import threading
import time

weather_bp = Blueprint('weather', __name__)
weather_service = WeatherService()

# Danh sách các thành phố để thu thập dữ liệu
CITIES = ["Ho Chi Minh City", "Hanoi", "Da Nang", "Can Tho", "Hue"]

@weather_bp.route('/weather/current', methods=['GET'])
def get_current_weather():
    """Lấy dữ liệu thời tiết hiện tại"""
    try:
        city = request.args.get('city', 'Ho Chi Minh City')
        weather_data = weather_service.get_weather_data(city)
        
        if weather_data:
            # Lưu vào database
            saved_record = weather_service.save_weather_data(weather_data)
            if saved_record:
                return jsonify({
                    'success': True,
                    'data': saved_record.to_dict()
                })
        
        return jsonify({
            'success': False,
            'message': 'Không thể lấy dữ liệu thời tiết'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500

@weather_bp.route('/weather/latest', methods=['GET'])
def get_latest_weather():
    """Lấy dữ liệu thời tiết mới nhất"""
    try:
        limit = request.args.get('limit', 10, type=int)
        latest_data = weather_service.get_latest_data(limit)
        
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in latest_data],
            'count': len(latest_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500

@weather_bp.route('/weather/city/<city_name>', methods=['GET'])
def get_city_weather(city_name):
    """Lấy dữ liệu thời tiết của một thành phố"""
    try:
        limit = request.args.get('limit', 24, type=int)
        city_data = weather_service.get_city_data(city_name, limit)
        
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in city_data],
            'city': city_name,
            'count': len(city_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500

@weather_bp.route('/weather/dashboard', methods=['GET'])
def get_dashboard_data():
    """Lấy dữ liệu cho dashboard"""
    try:
        dashboard_data = {}
        
        # Lấy dữ liệu mới nhất cho mỗi thành phố
        for city in CITIES:
            city_data = weather_service.get_city_data(city, 1)
            if city_data:
                dashboard_data[city] = city_data[0].to_dict()
        
        # Thống kê tổng quan
        total_records = WeatherData.query.count()
        
        return jsonify({
            'success': True,
            'cities_data': dashboard_data,
            'statistics': {
                'total_records': total_records,
                'cities_count': len(CITIES),
                'last_updated': max([data['timestamp'] for data in dashboard_data.values()]) if dashboard_data else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500

@weather_bp.route('/weather/collect', methods=['POST'])
def collect_weather_data():
    """Thu thập dữ liệu thời tiết cho tất cả thành phố"""
    try:
        collected_data = []
        
        for city in CITIES:
            weather_data = weather_service.get_weather_data(city)
            if weather_data:
                saved_record = weather_service.save_weather_data(weather_data)
                if saved_record:
                    collected_data.append(saved_record.to_dict())
        
        return jsonify({
            'success': True,
            'message': f'Đã thu thập dữ liệu cho {len(collected_data)} thành phố',
            'data': collected_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500

# Background task để thu thập dữ liệu định kỳ
def background_data_collection(app, realtime_service=None):
    """Thu thập dữ liệu thời tiết định kỳ (mỗi 2 phút cho thời gian thực)"""
    while True:
        try:
            with app.app_context():
                collected_count = 0
                for city in CITIES:
                    weather_data = weather_service.get_weather_data(city)
                    if weather_data:
                        saved_record = weather_service.save_weather_data(weather_data)
                        if saved_record:
                            collected_count += 1
                            # Phát sóng dữ liệu mới qua WebSocket ngay lập tức
                            if realtime_service:
                                realtime_service.broadcast_new_weather_data(saved_record)
                
                from datetime import datetime
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                message = f"Real-time data updated for {collected_count} cities at {current_time}"
                print(message)
                
                # Phát sóng thông báo thời gian thực
                if realtime_service:
                    realtime_service.broadcast_status(message, 'success')
                
        except Exception as e:
            error_msg = f"Real-time data collection error: {e}"
            print(error_msg)
            if realtime_service:
                realtime_service.broadcast_status(error_msg, 'error')
        
        # Chờ 2 phút cho cập nhật thời gian thực
        time.sleep(120)

# Khởi động background task
def start_background_collection(app, realtime_service=None):
    """Khởi động thu thập dữ liệu tự động"""
    collection_thread = threading.Thread(target=background_data_collection, args=(app, realtime_service), daemon=True)
    collection_thread.start()
    print("Started automatic data collection")
    
    # Khởi động realtime updates
    if realtime_service:
        realtime_service.start_realtime_updates()