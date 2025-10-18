"""
Simulation Service - Generates realistic F1 telemetry data
Uses NumPy for efficient numerical computations
"""
import time
import math
import numpy as np
from typing import Dict, List
from models import (
    CarTelemetry, Position, TireCompound, WeatherZone, 
    WeatherCondition, TrackPoint
)
from track_data import TRACK_CONFIG, TEAMS, DRIVER_NAMES


class CarState:
    """Internal state for each simulated car"""
    def __init__(self, car_id: str, start_progress: float):
        self.car_id = car_id
        self.track_progress = start_progress
        self.speed = 80 + np.random.random() * 20
        self.acceleration = 0.0
        self.target_speed = 280 + np.random.random() * 40
        self.last_update_time = time.time()
        self.pit_stop_cooldown = 0


class SimulationService:
    """
    High-performance simulation service using NumPy
    Generates realistic F1 race telemetry
    """
    
    def __init__(self):
        self.cars: Dict[str, CarState] = {}
        self.track_points: List[TrackPoint] = TRACK_CONFIG.track_points
        self.session_start_time = time.time()
        self.current_lap = 1
        self._initialize_cars()
    
    def _initialize_cars(self):
        """Initialize all cars with starting positions"""
        for idx, driver_name in enumerate(DRIVER_NAMES):
            car_id = f"CAR_{idx + 1}"
            # Stagger starting positions (grid formation)
            start_progress = -0.002 * idx
            self.cars[car_id] = CarState(car_id, start_progress)
    
    def _get_position_from_progress(self, progress: float) -> Position:
        """Convert track progress (0-1) to x,y coordinates"""
        # Normalize progress
        progress = progress % 1.0
        if progress < 0:
            progress += 1.0
        
        # Get track point index
        index = int(progress * len(self.track_points))
        next_index = (index + 1) % len(self.track_points)
        
        point = self.track_points[index]
        next_point = self.track_points[next_index]
        
        # Interpolate for smooth movement
        local_progress = (progress * len(self.track_points)) % 1.0
        
        return Position(
            x=point.x + (next_point.x - point.x) * local_progress,
            y=point.y + (next_point.y - point.y) * local_progress
        )
    
    def _get_sector_from_progress(self, progress: float) -> int:
        """Get current sector from track progress"""
        progress = progress % 1.0
        if progress < 0:
            progress += 1.0
        
        index = int(progress * len(self.track_points))
        if 0 <= index < len(self.track_points):
            return self.track_points[index].sector
        return 1
    
    def _calculate_speed_for_position(
        self, 
        progress: float, 
        current_speed: float
    ) -> float:
        """
        Calculate realistic speed based on track position
        Simulates acceleration zones and braking zones
        """
        sector = self._get_sector_from_progress(progress)
        sector_progress = (progress % (1/3)) * 3
        
        # Different speed profiles per sector
        if sector == 1:
            # Long straight, then hard braking
            target_speed = 320 if sector_progress < 0.4 else 180 - sector_progress * 200
        elif sector == 2:
            # Technical section with medium speed corners
            target_speed = 220 + math.sin(sector_progress * math.pi * 4) * 50
        else:
            # Slow chicane and acceleration zone
            target_speed = 160 + sector_progress * 140
        
        # Add realistic variation
        target_speed += (np.random.random() - 0.5) * 20
        
        # Smooth acceleration/deceleration
        max_accel_change = 15
        speed_diff = target_speed - current_speed
        actual_change = np.clip(speed_diff, -max_accel_change, max_accel_change)
        
        return np.clip(current_speed + actual_change, 50, 340)
    
    def update_telemetry(self) -> List[CarTelemetry]:
        """
        Update all car telemetry - main simulation loop
        Returns list of current telemetry for all cars
        """
        now = time.time()
        telemetry_data: List[CarTelemetry] = []
        
        for car_id, car_state in self.cars.items():
            delta_time = now - car_state.last_update_time
            car_state.last_update_time = now
            
            # Update speed based on track position
            car_state.speed = self._calculate_speed_for_position(
                car_state.track_progress,
                car_state.speed
            )
            
            # Calculate distance traveled
            progress_increment = (car_state.speed / 3.6) * delta_time / TRACK_CONFIG.total_length
            car_state.track_progress += progress_increment
            
            # Handle lap completion
            if car_state.track_progress >= 1:
                car_state.track_progress -= 1
                self.current_lap += 1
            
            # Get current position and sector
            position = self._get_position_from_progress(car_state.track_progress)
            sector = self._get_sector_from_progress(car_state.track_progress)
            
            # Simulate pit stops (very rare)
            in_pit = car_state.pit_stop_cooldown > 0
            if in_pit:
                car_state.pit_stop_cooldown -= 1
            elif np.random.random() < 0.0001:
                car_state.pit_stop_cooldown = 100
            
            # Determine tire compound based on lap
            lap_number = int(car_state.track_progress) + 1
            if lap_number < 15:
                tire = TireCompound.SOFT
            elif lap_number < 35:
                tire = TireCompound.MEDIUM
            else:
                tire = TireCompound.HARD
            
            # DRS eligibility
            drs_available = np.random.random() < 0.3
            drs_enabled = drs_available and car_state.speed > 250
            
            # Get team assignment
            car_index = int(car_id.split('_')[1]) - 1
            team_id = TEAMS[car_index % len(TEAMS)].id
            driver_name = DRIVER_NAMES[car_index]
            
            # Simulate lap time (1:20 - 1:35)
            lap_time = 80000 + np.random.random() * 15000
            
            telemetry = CarTelemetry(
                id=car_id,
                driver_name=driver_name,
                team_id=team_id,
                position=position,
                speed=round(car_state.speed),
                tire=tire,
                tire_laps=lap_number % 20,
                fuel=max(10, 100 - lap_number * 1.5),
                lap_time=round(lap_time),
                current_lap=lap_number,
                sector=sector,
                in_pit=in_pit,
                drs_enabled=drs_enabled,
                drs_available=drs_available,
                timestamp=now
            )
            
            telemetry_data.append(telemetry)
        
        return telemetry_data
    
    def generate_weather_data(self) -> List[WeatherZone]:
        """Generate simulated weather data for all sectors"""
        conditions = [WeatherCondition.DRY, WeatherCondition.DAMP, WeatherCondition.WET]
        base_condition = conditions[np.random.randint(0, len(conditions))]
        
        weather_zones = []
        for sector in TRACK_CONFIG.sectors:
            # Occasionally have different conditions in different sectors
            condition = base_condition
            if np.random.random() < 0.1:
                condition = conditions[np.random.randint(0, len(conditions))]
            
            rain_intensity = {
                WeatherCondition.DRY: 0,
                WeatherCondition.DAMP: 20,
                WeatherCondition.WET: 60,
                WeatherCondition.HEAVY_RAIN: 90
            }.get(condition, 0)
            
            grip_level = {
                WeatherCondition.DRY: 95,
                WeatherCondition.DAMP: 75,
                WeatherCondition.WET: 50,
                WeatherCondition.HEAVY_RAIN: 30
            }.get(condition, 95)
            
            weather_zone = WeatherZone(
                sector_id=sector.id,
                condition=condition,
                temperature=20 + np.random.random() * 10,
                track_temp=25 + np.random.random() * 20,
                humidity=40 + np.random.random() * 40,
                wind_speed=5 + np.random.random() * 15,
                wind_direction=np.random.random() * 360,
                rain_intensity=rain_intensity,
                grip_level=grip_level
            )
            weather_zones.append(weather_zone)
        
        return weather_zones
    
    def reset(self):
        """Reset simulation to initial state"""
        self.cars.clear()
        self.current_lap = 1
        self.session_start_time = time.time()
        self._initialize_cars()
    
    def get_session_info(self) -> Dict:
        """Get current session information"""
        return {
            "current_lap": self.current_lap,
            "session_time": int(time.time() - self.session_start_time),
            "total_cars": len(self.cars)
        }

