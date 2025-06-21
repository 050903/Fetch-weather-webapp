from flask_socketio import emit
import threading
import time
from src.services.weather_service import WeatherService

class RealtimeService:
    def __init__(self, socketio):
        self.socketio = socketio
        self.weather_service = WeatherService()
        self.connected_clients = set()
        self.setup_socketio_events()
    
    def setup_socketio_events(self):
        """Thiết lập các sự kiện SocketIO"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            self.connected_clients.add('client')
            emit('status', {'message': 'Kết nối thành công', 'type': 'success'})
            
            # Gửi dữ liệu ban đầu
            self.send_initial_data()
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')
            self.connected_clients.discard('client')
        
        @self.socketio.on('request_data')
        def handle_request_data(data):
            """Xử lý yêu cầu dữ liệu từ client"""
            data_type = data.get('type', 'dashboard')
            
            if data_type == 'dashboard':
                self.send_dashboard_data()
            elif data_type == 'latest':
                self.send_latest_data()
            elif data_type == 'city':
                city = data.get('city', 'Ho Chi Minh City')
                self.send_city_data(city)
    
    def send_initial_data(self):
        """Gửi dữ liệu ban đầu khi client kết nối"""
        try:
            # Gửi dữ liệu dashboard
            self.send_dashboard_data()
            
            # Gửi dữ liệu mới nhất
            self.send_latest_data()
            
        except Exception as e:
            print(f"Initial data send error: {e}")
    
    def send_dashboard_data(self):
        """Gửi dữ liệu dashboard"""
        try:
            cities = ["Ho Chi Minh City", "Hanoi", "Da Nang", "Can Tho", "Hue"]
            dashboard_data = {}
            
            for city in cities:
                city_data = self.weather_service.get_city_data(city, 1)
                if city_data:
                    dashboard_data[city] = city_data[0].to_dict()
            
            from src.models.weather import WeatherData
            total_records = WeatherData.query.count()
            
            data = {
                'cities_data': dashboard_data,
                'statistics': {
                    'total_records': total_records,
                    'cities_count': len(cities),
                    'last_updated': max([data['timestamp'] for data in dashboard_data.values()]) if dashboard_data else None
                }
            }
            
            self.socketio.emit('dashboard_update', data)
            
        except Exception as e:
            print(f"Dashboard data send error: {e}")
    
    def send_latest_data(self, limit=20):
        """Gửi dữ liệu mới nhất"""
        try:
            latest_data = self.weather_service.get_latest_data(limit)
            data = [record.to_dict() for record in latest_data]
            
            self.socketio.emit('latest_data_update', {
                'data': data,
                'count': len(data)
            })
            
        except Exception as e:
            print(f"Latest data send error: {e}")
    
    def send_city_data(self, city, limit=24):
        """Gửi dữ liệu của một thành phố"""
        try:
            city_data = self.weather_service.get_city_data(city, limit)
            data = [record.to_dict() for record in city_data]
            
            self.socketio.emit('city_data_update', {
                'city': city,
                'data': data,
                'count': len(data)
            })
            
        except Exception as e:
            print(f"City data send error: {e}")
    
    def broadcast_new_weather_data(self, weather_data):
        """Phát sóng dữ liệu thời tiết mới"""
        try:
            if len(self.connected_clients) > 0:
                self.socketio.emit('new_weather_data', {
                    'data': weather_data.to_dict() if hasattr(weather_data, 'to_dict') else weather_data,
                    'timestamp': time.time()
                })
                
                # Cập nhật dashboard
                self.send_dashboard_data()
                
        except Exception as e:
            print(f"New data broadcast error: {e}")
    
    def broadcast_status(self, message, status_type='info'):
        """Phát sóng thông báo trạng thái"""
        try:
            if len(self.connected_clients) > 0:
                self.socketio.emit('status_update', {
                    'message': message,
                    'type': status_type,
                    'timestamp': time.time()
                })
                
        except Exception as e:
            print(f"Status broadcast error: {e}")
    
    def start_realtime_updates(self):
        """Khởi động cập nhật dữ liệu theo thời gian thực chính xác"""
        def realtime_worker():
            while True:
                try:
                    if len(self.connected_clients) > 0:
                        from datetime import datetime
                        current_time = datetime.now()
                        
                        # Cập nhật dữ liệu mới nhất mỗi 15 giây
                        self.send_latest_data()
                        
                        # Gửi timestamp chính xác
                        self.socketio.emit('time_update', {
                            'current_time': current_time.isoformat(),
                            'timestamp': time.time()
                        })
                        
                        time.sleep(15)
                        
                        # Cập nhật dashboard mỗi 30 giây
                        if len(self.connected_clients) > 0:
                            self.send_dashboard_data()
                        
                        time.sleep(15)
                    else:
                        time.sleep(5)  # Kiểm tra kết nối thường xuyên hơn
                        
                except Exception as e:
                    print(f"Realtime worker error: {e}")
                    time.sleep(5)
        
        # Khởi động thread cho realtime updates
        realtime_thread = threading.Thread(target=realtime_worker, daemon=True)
        realtime_thread.start()
        print("Started high-frequency realtime updates")
    
    def get_connected_clients_count(self):
        """Lấy số lượng client đang kết nối"""
        return len(self.connected_clients)