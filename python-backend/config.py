"""
Configuration settings for F1 Race Strategy Platform
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 3001
    RELOAD: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Simulation Configuration
    UPDATE_FREQUENCY: float = 0.05  # 50ms = 20Hz
    TOTAL_LAPS: int = 50
    NUM_CARS: int = 20
    
    # Detection Configuration
    SLOWDOWN_THRESHOLD: float = 0.3  # 30% speed drop
    PIT_CONGESTION_THRESHOLD: int = 3
    ALERT_COOLDOWN: float = 5.0  # seconds
    
    # FastF1 Configuration
    FASTF1_CACHE_DIR: str = "./cache/fastf1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

