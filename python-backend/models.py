"""
Data models for F1 Race Strategy Platform
Shared type definitions matching frontend TypeScript types
"""
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums and Type Aliases
# ============================================================================

class TireCompound(str, Enum):
    SOFT = "soft"
    MEDIUM = "medium"
    HARD = "hard"
    INTERMEDIATE = "intermediate"
    WET = "wet"


class WeatherCondition(str, Enum):
    DRY = "dry"
    DAMP = "damp"
    WET = "wet"
    HEAVY_RAIN = "heavy_rain"


class FlagType(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    DOUBLE_YELLOW = "double_yellow"
    RED = "red"
    BLUE = "blue"
    WHITE = "white"


class SessionType(str, Enum):
    PRACTICE = "practice"
    QUALIFYING = "qualifying"
    SPRINT = "sprint"
    RACE = "race"


class SessionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    FINISHED = "finished"


class AlertType(str, Enum):
    SLOWDOWN = "slowdown"
    WEATHER = "weather"
    PIT_CONGESTION = "pit_congestion"
    INCIDENT = "incident"
    STRATEGY = "strategy"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class IncidentType(str, Enum):
    COLLISION = "collision"
    SPIN = "spin"
    DEBRIS = "debris"
    MECHANICAL = "mechanical"
    SLOWDOWN = "slowdown"


# ============================================================================
# Core Models
# ============================================================================

class Position(BaseModel):
    """2D position coordinates"""
    x: float
    y: float


class TrackPoint(BaseModel):
    """Point on the racing track"""
    x: float
    y: float
    sector: int


class Sector(BaseModel):
    """Track sector definition"""
    id: int
    name: str
    start_index: int = Field(..., alias='startIndex')
    end_index: int = Field(..., alias='endIndex')
    length: float  # meters
    
    class Config:
        populate_by_name = True


class DRSZone(BaseModel):
    """DRS zone definition"""
    id: str
    detection_point: float = Field(..., alias='detectionPoint')  # track percentage
    activation_point: float = Field(..., alias='activationPoint')
    end_point: float = Field(..., alias='endPoint')
    
    class Config:
        populate_by_name = True


class TrackConfig(BaseModel):
    """Complete track configuration"""
    name: str
    country: str
    total_length: float = Field(..., alias='totalLength')  # meters
    sectors: List[Sector]
    drs_zones: List[DRSZone] = Field(..., alias='drsZones')
    pit_entry: Position = Field(..., alias='pitEntry')
    pit_exit: Position = Field(..., alias='pitExit')
    start_line: Position = Field(..., alias='startLine')
    track_points: List[TrackPoint] = Field(..., alias='trackPoints')
    
    class Config:
        populate_by_name = True


class Team(BaseModel):
    """F1 team information"""
    id: str
    name: str
    color: str


class CarTelemetry(BaseModel):
    """Real-time car telemetry data"""
    id: str
    driver_name: str = Field(..., alias='driverName')
    team_id: str = Field(..., alias='teamId')
    position: Position
    speed: float  # km/h
    tire: TireCompound
    tire_laps: int = Field(..., alias='tireLaps')
    fuel: float  # percentage
    lap_time: float = Field(..., alias='lapTime')  # milliseconds
    current_lap: int = Field(..., alias='currentLap')
    sector: int
    in_pit: bool = Field(..., alias='inPit')
    drs_enabled: bool = Field(..., alias='drsEnabled')
    drs_available: bool = Field(..., alias='drsAvailable')
    timestamp: float
    
    class Config:
        populate_by_name = True


class WeatherZone(BaseModel):
    """Weather conditions for a track sector"""
    sector_id: int = Field(..., alias='sectorId')
    condition: WeatherCondition
    temperature: float  # Celsius
    track_temp: float = Field(..., alias='trackTemp')  # Celsius
    humidity: float  # percentage
    wind_speed: float = Field(..., alias='windSpeed')  # km/h
    wind_direction: float = Field(..., alias='windDirection')  # degrees
    rain_intensity: float = Field(..., alias='rainIntensity')  # 0-100
    grip_level: float = Field(..., alias='gripLevel')  # 0-100
    
    class Config:
        populate_by_name = True


class RaceFlag(BaseModel):
    """Race flag status"""
    type: FlagType
    sector: Optional[int] = None
    timestamp: float
    active: bool


class Alert(BaseModel):
    """Alert/warning message"""
    id: str
    type: AlertType
    severity: AlertSeverity
    message: str
    car_id: Optional[str] = Field(None, alias='carId')
    sector: Optional[int] = None
    timestamp: float
    acknowledged: bool = False
    
    class Config:
        populate_by_name = True


class Incident(BaseModel):
    """Track incident"""
    id: str
    type: IncidentType
    car_id: str = Field(..., alias='carId')
    position: Position
    sector: int
    timestamp: float
    severity: Literal["low", "medium", "high"]
    description: str
    
    class Config:
        populate_by_name = True


class PitStop(BaseModel):
    """Pit stop event"""
    car_id: str
    lap_number: int
    duration: float  # milliseconds
    tire_from: TireCompound
    tire_to: TireCompound
    timestamp: float


class RaceSession(BaseModel):
    """Race session state"""
    session_id: str = Field(..., alias='sessionId')
    session_type: SessionType = Field(..., alias='sessionType')
    track_config: TrackConfig = Field(..., alias='trackConfig')
    total_laps: int = Field(..., alias='totalLaps')
    current_lap: int = Field(..., alias='currentLap')
    session_time: float = Field(..., alias='sessionTime')  # seconds
    session_status: SessionStatus = Field(..., alias='sessionStatus')
    weather: List[WeatherZone]
    flags: List[RaceFlag]
    
    class Config:
        populate_by_name = True


class StrategyRecommendation(BaseModel):
    """AI-generated strategy recommendation"""
    car_id: str
    recommendation: str
    pit_window_start: int
    pit_window_end: int
    recommended_tire: TireCompound
    confidence: float  # 0-100
    reasoning: List[str]


# ============================================================================
# WebSocket Messages
# ============================================================================

class MessageType(str, Enum):
    TELEMETRY_UPDATE = "telemetry_update"
    WEATHER_UPDATE = "weather_update"
    INCIDENT = "incident"
    ALERT = "alert"
    FLAG_CHANGE = "flag_change"
    PIT_STOP = "pit_stop"
    SESSION_UPDATE = "session_update"
    STRATEGY_RECOMMENDATION = "strategy_recommendation"


class WebSocketMessage(BaseModel):
    """WebSocket message wrapper"""
    type: MessageType
    timestamp: float
    data: Dict


# ============================================================================
# API Request/Response Models
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: float


class SessionInfoResponse(BaseModel):
    """Session information response"""
    session: RaceSession
    current_lap: int
    session_time: float
    total_cars: int
    is_active: bool


class ActionResponse(BaseModel):
    """Generic action response"""
    success: bool
    message: str

