"""
F1 Race Strategy Platform - Python Backend Server
FastAPI + Socket.IO for real-time race monitoring
"""
import asyncio
import time
from typing import Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from config import settings
from models import (
    HealthResponse, SessionInfoResponse, ActionResponse,
    CarTelemetry, WeatherZone, Alert, Incident,
    RaceSession, SessionStatus, SessionType, RaceFlag, FlagType,
    WebSocketMessage, MessageType
)
from track_data import TRACK_CONFIG, TEAMS
from simulation_service import SimulationService
from detection_service import DetectionService


# ============================================================================
# Application State
# ============================================================================

class AppState:
    """Global application state"""
    def __init__(self):
        self.simulation_service = SimulationService()
        self.detection_service = DetectionService()
        self.is_session_active = False
        self.update_task: asyncio.Task = None
        self.weather_task: asyncio.Task = None
        
        # Race session
        self.race_session = RaceSession(
            session_id=f"session_{int(time.time())}",
            session_type=SessionType.RACE,
            track_config=TRACK_CONFIG,
            total_laps=settings.TOTAL_LAPS,
            current_lap=1,
            session_time=0,
            session_status=SessionStatus.NOT_STARTED,
            weather=self.simulation_service.generate_weather_data(),
            flags=[RaceFlag(type=FlagType.GREEN, active=True, timestamp=time.time())]
        )


app_state = AppState()


# ============================================================================
# Socket.IO Server
# ============================================================================

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.ALLOWED_ORIGINS,
    logger=True,
    engineio_logger=False
)


# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    print("\n" + "="*65)
    print("║   F1 Race Strategy Platform - Python Backend Server        ║")
    print("="*65)
    print(f"║   Server running on: http://{settings.HOST}:{settings.PORT}")
    print(f"║   WebSocket endpoint: ws://{settings.HOST}:{settings.PORT}")
    print("║   Ready to receive connections...")
    print("="*65 + "\n")
    yield
    # Cleanup
    if app_state.is_session_active:
        await stop_session()


app = FastAPI(
    title="F1 Race Strategy Platform API",
    description="Real-time F1 race monitoring with HPC integration",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app
)


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", timestamp=time.time())


@app.get("/api/track")
async def get_track():
    """Get track configuration"""
    return TRACK_CONFIG


@app.get("/api/teams")
async def get_teams():
    """Get teams data"""
    return TEAMS


@app.get("/api/session", response_model=SessionInfoResponse)
async def get_session():
    """Get current session information"""
    session_info = app_state.simulation_service.get_session_info()
    return SessionInfoResponse(
        session=app_state.race_session,
        current_lap=session_info["current_lap"],
        session_time=session_info["session_time"],
        total_cars=session_info["total_cars"],
        is_active=app_state.is_session_active
    )


@app.post("/api/session/start", response_model=ActionResponse)
async def start_session_endpoint():
    """Start race session"""
    if not app_state.is_session_active:
        await start_session()
        return ActionResponse(success=True, message="Session started")
    return ActionResponse(success=False, message="Session already active")


@app.post("/api/session/stop", response_model=ActionResponse)
async def stop_session_endpoint():
    """Stop race session"""
    if app_state.is_session_active:
        await stop_session()
        return ActionResponse(success=True, message="Session stopped")
    return ActionResponse(success=False, message="No active session")


@app.post("/api/session/reset", response_model=ActionResponse)
async def reset_session_endpoint():
    """Reset race session"""
    await stop_session()
    app_state.simulation_service.reset()
    app_state.detection_service.reset()
    app_state.race_session.current_lap = 1
    app_state.race_session.session_time = 0
    app_state.race_session.session_status = SessionStatus.NOT_STARTED
    return ActionResponse(success=True, message="Session reset")


# ============================================================================
# WebSocket Event Handlers
# ============================================================================

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f"✅ Client connected: {sid}")
    
    # Send initial data
    await sio.emit('session_update', {
        'type': MessageType.SESSION_UPDATE.value,
        'timestamp': time.time(),
        'data': app_state.race_session.model_dump(by_alias=True)
    }, room=sid)
    
    await sio.emit('track_config', {
        'type': MessageType.SESSION_UPDATE.value,
        'timestamp': time.time(),
        'data': TRACK_CONFIG.model_dump(by_alias=True)
    }, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"❌ Client disconnected: {sid}")


@sio.event
async def start_session(sid):
    """Handle start session request"""
    if not app_state.is_session_active:
        await start_session()


@sio.event
async def stop_session(sid):
    """Handle stop session request"""
    if app_state.is_session_active:
        await stop_session()


@sio.event
async def reset_session(sid):
    """Handle reset session request"""
    await stop_session()
    app_state.simulation_service.reset()
    app_state.detection_service.reset()


# ============================================================================
# Session Management
# ============================================================================

async def start_session():
    """Start the race session and begin broadcasting"""
    if app_state.is_session_active:
        return
    
    print("🏁 Starting race session...")
    app_state.is_session_active = True
    app_state.race_session.session_status = SessionStatus.IN_PROGRESS
    
    # Broadcast session start
    session_data = app_state.race_session.model_dump(by_alias=True)
    session_data['sessionStatus'] = SessionStatus.IN_PROGRESS.value
    
    await sio.emit('session_update', {
        'type': MessageType.SESSION_UPDATE.value,
        'timestamp': time.time(),
        'data': session_data
    })
    
    # Start update loops
    app_state.update_task = asyncio.create_task(telemetry_update_loop())
    app_state.weather_task = asyncio.create_task(weather_update_loop())


async def stop_session():
    """Stop the race session"""
    if not app_state.is_session_active:
        return
    
    print("⏸️  Stopping race session...")
    app_state.is_session_active = False
    app_state.race_session.session_status = SessionStatus.PAUSED
    
    # Cancel update tasks
    if app_state.update_task:
        app_state.update_task.cancel()
        app_state.update_task = None
    
    if app_state.weather_task:
        app_state.weather_task.cancel()
        app_state.weather_task = None
    
    # Broadcast session stop
    session_data = app_state.race_session.model_dump(by_alias=True)
    session_data['sessionStatus'] = SessionStatus.PAUSED.value
    
    await sio.emit('session_update', {
        'type': MessageType.SESSION_UPDATE.value,
        'timestamp': time.time(),
        'data': session_data
    })


# ============================================================================
# Background Update Loops
# ============================================================================

async def telemetry_update_loop():
    """
    Main telemetry update loop
    Runs at configured frequency (default 20Hz)
    """
    print(f"📡 Starting telemetry broadcast at {1/settings.UPDATE_FREQUENCY:.0f}Hz")
    
    while app_state.is_session_active:
        try:
            # Update simulation
            telemetry_data = app_state.simulation_service.update_telemetry()
            session_info = app_state.simulation_service.get_session_info()
            
            # Update session info
            app_state.race_session.current_lap = session_info["current_lap"]
            app_state.race_session.session_time = session_info["session_time"]
            
            # Run detection algorithms
            alerts, incidents = app_state.detection_service.process_detections(
                telemetry_data,
                app_state.race_session.weather
            )
            
            # Broadcast telemetry (convert to camelCase for frontend)
            await sio.emit('telemetry_update', {
                'type': MessageType.TELEMETRY_UPDATE.value,
                'timestamp': time.time(),
                'data': [car.model_dump(by_alias=True) for car in telemetry_data]
            })
            
            # Broadcast alerts
            for alert in alerts:
                await sio.emit('alert', {
                    'type': MessageType.ALERT.value,
                    'timestamp': time.time(),
                    'data': alert.model_dump(by_alias=True)
                })
            
            # Broadcast incidents
            for incident in incidents:
                await sio.emit('incident', {
                    'type': MessageType.INCIDENT.value,
                    'timestamp': time.time(),
                    'data': incident.model_dump(by_alias=True)
                })
            
            # Sleep for update frequency
            await asyncio.sleep(settings.UPDATE_FREQUENCY)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"❌ Error in telemetry loop: {e}")
            await asyncio.sleep(settings.UPDATE_FREQUENCY)


async def weather_update_loop():
    """
    Weather update loop
    Updates every 10 seconds
    """
    while app_state.is_session_active:
        try:
            await asyncio.sleep(10)
            
            # Generate new weather data
            weather = app_state.simulation_service.generate_weather_data()
            app_state.race_session.weather = weather
            
            # Broadcast weather update
            await sio.emit('weather_update', {
                'type': MessageType.WEATHER_UPDATE.value,
                'timestamp': time.time(),
                'data': [w.model_dump(by_alias=True) for w in weather]
            })
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"❌ Error in weather loop: {e}")
            await asyncio.sleep(10)


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "server:socket_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )

