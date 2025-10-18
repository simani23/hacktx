"""
Detection Service - Analyzes telemetry for events and anomalies
Modular design allows easy addition of new detection algorithms
"""
import time
import uuid
from typing import Dict, List, Tuple
from models import (
    Alert, Incident, CarTelemetry, WeatherZone,
    AlertType, AlertSeverity, IncidentType
)
from config import settings


class DetectionService:
    """
    Extensible detection service for race event analysis
    Implements various detection modules
    """
    
    def __init__(self):
        self.previous_telemetry: Dict[str, CarTelemetry] = {}
        self.alert_history: Dict[str, float] = {}
        self.alert_cooldown = settings.ALERT_COOLDOWN
    
    def process_detections(
        self,
        cars: List[CarTelemetry],
        weather: List[WeatherZone]
    ) -> Tuple[List[Alert], List[Incident]]:
        """
        Process all detection modules
        Returns alerts and incidents
        """
        alerts: List[Alert] = []
        incidents: List[Incident] = []
        
        # Run detection modules
        alerts.extend(self._detect_slowdowns(cars))
        alerts.extend(self._detect_pit_congestion(cars))
        alerts.extend(self._detect_weather_issues(weather))
        
        detected_incidents = self._detect_incidents(cars)
        incidents.extend(detected_incidents)
        
        # Convert incidents to alerts
        alerts.extend(self._incidents_to_alerts(detected_incidents))
        
        # Update history
        for car in cars:
            self.previous_telemetry[car.id] = car
        
        return alerts, incidents
    
    def _detect_slowdowns(self, cars: List[CarTelemetry]) -> List[Alert]:
        """
        Detection Module: Slowdown Detection
        Detects cars with significant speed reduction
        """
        alerts: List[Alert] = []
        now = time.time()
        
        for car in cars:
            prev_car = self.previous_telemetry.get(car.id)
            if not prev_car:
                continue
            
            speed_drop = prev_car.speed - car.speed
            speed_drop_pct = (speed_drop / prev_car.speed) if prev_car.speed > 0 else 0
            
            # Alert if speed drops >30% and car is not in pit
            if speed_drop_pct > 0.3 and car.speed < 150 and not car.in_pit:
                alert_key = f"slowdown_{car.id}"
                last_alert = self.alert_history.get(alert_key, 0)
                
                if now - last_alert > self.alert_cooldown:
                    severity = AlertSeverity.CRITICAL if speed_drop_pct > 0.5 else AlertSeverity.WARNING
                    
                    alerts.append(Alert(
                        id=str(uuid.uuid4()),
                        type=AlertType.SLOWDOWN,
                        severity=severity,
                        message=f"{car.driver_name} experiencing significant slowdown in Sector {car.sector}",
                        car_id=car.id,
                        sector=car.sector,
                        timestamp=now,
                        acknowledged=False
                    ))
                    self.alert_history[alert_key] = now
        
        return alerts
    
    def _detect_pit_congestion(self, cars: List[CarTelemetry]) -> List[Alert]:
        """
        Detection Module: Pit Lane Congestion
        Detects when multiple cars are pitting simultaneously
        """
        alerts: List[Alert] = []
        cars_in_pit = [car for car in cars if car.in_pit]
        now = time.time()
        
        if len(cars_in_pit) >= settings.PIT_CONGESTION_THRESHOLD:
            alert_key = "pit_congestion"
            last_alert = self.alert_history.get(alert_key, 0)
            
            if now - last_alert > self.alert_cooldown:
                severity = AlertSeverity.CRITICAL if len(cars_in_pit) >= 5 else AlertSeverity.WARNING
                
                alerts.append(Alert(
                    id=str(uuid.uuid4()),
                    type=AlertType.PIT_CONGESTION,
                    severity=severity,
                    message=f"Pit lane congestion: {len(cars_in_pit)} cars currently pitting",
                    timestamp=now,
                    acknowledged=False
                ))
                self.alert_history[alert_key] = now
        
        return alerts
    
    def _detect_weather_issues(self, weather: List[WeatherZone]) -> List[Alert]:
        """
        Detection Module: Weather Issues
        Detects adverse weather conditions
        """
        alerts: List[Alert] = []
        now = time.time()
        
        for zone in weather:
            # Alert on wet conditions
            if zone.condition in ["wet", "heavy_rain"]:
                alert_key = f"weather_sector_{zone.sector_id}"
                last_alert = self.alert_history.get(alert_key, 0)
                
                if now - last_alert > self.alert_cooldown * 2:
                    severity = (AlertSeverity.CRITICAL if zone.condition == "heavy_rain" 
                               else AlertSeverity.WARNING)
                    
                    condition_text = zone.condition.replace("_", " ").upper()
                    alerts.append(Alert(
                        id=str(uuid.uuid4()),
                        type=AlertType.WEATHER,
                        severity=severity,
                        message=f"{condition_text} conditions in Sector {zone.sector_id} - Grip at {zone.grip_level:.0f}%",
                        sector=zone.sector_id,
                        timestamp=now,
                        acknowledged=False
                    ))
                    self.alert_history[alert_key] = now
            
            # Alert on low grip
            if zone.grip_level < 60:
                alert_key = f"grip_sector_{zone.sector_id}"
                last_alert = self.alert_history.get(alert_key, 0)
                
                if now - last_alert > self.alert_cooldown * 2:
                    alerts.append(Alert(
                        id=str(uuid.uuid4()),
                        type=AlertType.WEATHER,
                        severity=AlertSeverity.INFO,
                        message=f"Low grip warning in Sector {zone.sector_id}: {zone.grip_level:.0f}%",
                        sector=zone.sector_id,
                        timestamp=now,
                        acknowledged=False
                    ))
                    self.alert_history[alert_key] = now
        
        return alerts
    
    def _detect_incidents(self, cars: List[CarTelemetry]) -> List[Incident]:
        """
        Detection Module: Incident Detection
        Detects potential track incidents
        """
        incidents: List[Incident] = []
        now = time.time()
        
        for car in cars:
            prev_car = self.previous_telemetry.get(car.id)
            if not prev_car:
                continue
            
            speed_drop = prev_car.speed - car.speed
            
            # Detect severe slowdowns as potential incidents
            if speed_drop > 100 and car.speed < 50 and not car.in_pit:
                incidents.append(Incident(
                    id=str(uuid.uuid4()),
                    type=IncidentType.SLOWDOWN,
                    car_id=car.id,
                    position=car.position,
                    sector=car.sector,
                    timestamp=now,
                    severity="high",
                    description=f"{car.driver_name} experienced sudden severe slowdown"
                ))
        
        return incidents
    
    def _incidents_to_alerts(self, incidents: List[Incident]) -> List[Alert]:
        """Convert incidents to alerts"""
        alerts = []
        for incident in incidents:
            severity_map = {"low": AlertSeverity.INFO, "medium": AlertSeverity.WARNING, "high": AlertSeverity.CRITICAL}
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                type=AlertType.INCIDENT,
                severity=severity_map.get(incident.severity, AlertSeverity.WARNING),
                message=incident.description,
                car_id=incident.car_id,
                sector=incident.sector,
                timestamp=incident.timestamp,
                acknowledged=False
            ))
        return alerts
    
    def reset(self):
        """Reset detection service state"""
        self.previous_telemetry.clear()
        self.alert_history.clear()

