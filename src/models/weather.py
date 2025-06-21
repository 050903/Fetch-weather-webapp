from datetime import datetime
from src.models.user import db

class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(10), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    feels_like = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    pressure = db.Column(db.Integer, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    wind_direction = db.Column(db.Integer, nullable=False)
    weather_main = db.Column(db.String(50), nullable=False)
    weather_description = db.Column(db.String(100), nullable=False)
    visibility = db.Column(db.Integer)
    uv_index = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'city': self.city,
            'country': self.country,
            'temperature': self.temperature,
            'feels_like': self.feels_like,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'weather_main': self.weather_main,
            'weather_description': self.weather_description,
            'visibility': self.visibility,
            'uv_index': self.uv_index
        }