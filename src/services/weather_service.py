import requests
import os
from datetime import datetime
from src.models.user import db
from src.models.weather import WeatherData

class WeatherService:
    def __init__(self):
        # Sử dụng API key miễn phí của OpenWeatherMap
        # Trong thực tế, bạn cần đăng ký tài khoản để lấy API key
        self.api_key = "demo_key"  # Thay thế bằng API key thực
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_weather_data(self, city="Ho Chi Minh City"):
        """Thu thập dữ liệu thời tiết cho một thành phố"""
        try:
            # Gọi API current weather
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'lang': 'vi'
            }
            
            # Sử dụng dữ liệu mẫu khi không có API key thực
            if self.api_key == "demo_key":
                return self._get_mock_data(city)
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_weather_data(data)
            
        except requests.exceptions.RequestException as e:
            print(f"API call error: {e}")
            return self._get_mock_data(city)
        except Exception as e:
            print(f"Data processing error: {e}")
            return None
    
    def _parse_weather_data(self, data):
        """Phân tích dữ liệu từ API response"""
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind'].get('speed', 0),
            'wind_direction': data['wind'].get('deg', 0),
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'visibility': data.get('visibility', 0),
            'uv_index': None  # Cần API call riêng cho UV index
        }
    
    def _get_mock_data(self, city):
        """Tạo dữ liệu mẫu cho demo với thời gian thực chính xác"""
        import random
        import time
        from datetime import datetime
        
        # Sử dụng timestamp hiện tại để tạo dữ liệu thay đổi theo thời gian
        current_time = datetime.now()
        time_factor = (current_time.minute + current_time.second / 60) / 60  # 0-1 based on current time
        
        cities_data = {
            "Ho Chi Minh City": {"country": "VN", "temp_base": 28},
            "Hanoi": {"country": "VN", "temp_base": 25},
            "Da Nang": {"country": "VN", "temp_base": 27},
            "Can Tho": {"country": "VN", "temp_base": 29},
            "Hue": {"country": "VN", "temp_base": 26}
        }
        
        city_info = cities_data.get(city, {"country": "VN", "temp_base": 27})
        # Nhiệt độ thay đổi theo thời gian thực
        temp_variation = 3 * (0.5 - time_factor) + random.uniform(-1, 1)
        temp = city_info["temp_base"] + temp_variation
        
        weather_conditions = [
            ("Clear", "trời quang"),
            ("Clouds", "có mây"),
            ("Rain", "mưa nhẹ"),
            ("Thunderstorm", "dông bão")
        ]
        
        # Thời tiết thay đổi dựa trên thời gian
        weather_index = int(time_factor * len(weather_conditions)) % len(weather_conditions)
        weather_main, weather_desc = weather_conditions[weather_index]
        
        return {
            'city': city,
            'country': city_info["country"],
            'temperature': round(temp, 1),
            'feels_like': round(temp + random.uniform(-2, 3), 1),
            'humidity': int(65 + 20 * time_factor + random.randint(-5, 5)),
            'pressure': int(1015 + 8 * (0.5 - time_factor) + random.randint(-2, 2)),
            'wind_speed': round(5 + 8 * time_factor + random.uniform(-1, 1), 1),
            'wind_direction': int((current_time.minute * 6 + random.randint(-30, 30)) % 360),
            'weather_main': weather_main,
            'weather_description': weather_desc,
            'visibility': int(9000 + 1000 * time_factor),
            'uv_index': round(3 + 5 * time_factor, 1)
        }
    
    def save_weather_data(self, weather_data):
        """Lưu dữ liệu thời tiết vào database"""
        try:
            weather_record = WeatherData(**weather_data)
            db.session.add(weather_record)
            db.session.commit()
            return weather_record
        except Exception as e:
            db.session.rollback()
            print(f"Data save error: {e}")
            return None
    
    def get_latest_data(self, limit=10):
        """Lấy dữ liệu thời tiết mới nhất"""
        try:
            return WeatherData.query.order_by(WeatherData.timestamp.desc()).limit(limit).all()
        except Exception as e:
            print(f"Data query error: {e}")
            return []
    
    def get_city_data(self, city, limit=24):
        """Lấy dữ liệu thời tiết của một thành phố"""
        try:
            return WeatherData.query.filter_by(city=city).order_by(WeatherData.timestamp.desc()).limit(limit).all()
        except Exception as e:
            print(f"City data query error: {e}")
            return []