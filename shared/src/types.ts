// ============================================================================
// CORE TYPES FOR F1 RACE STRATEGY PLATFORM
// ============================================================================

// ---------------------------------------------------------------------------
// Car & Telemetry Types
// ---------------------------------------------------------------------------

export interface Position {
  x: number;
  y: number;
}

export type TireCompound = 'soft' | 'medium' | 'hard' | 'intermediate' | 'wet';

export type TeamColor = string;

export interface Team {
  id: string;
  name: string;
  color: TeamColor;
}

export interface CarTelemetry {
  id: string;
  driverName: string;
  teamId: string;
  position: Position;
  speed: number; // km/h
  tire: TireCompound;
  tireLaps: number;
  fuel: number; // percentage
  lapTime: number; // milliseconds
  currentLap: number;
  sector: number; // 1, 2, or 3
  inPit: boolean;
  drsEnabled: boolean;
  drsAvailable: boolean;
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Track Types
// ---------------------------------------------------------------------------

export interface TrackPoint {
  x: number;
  y: number;
  sector: number;
}

export interface Sector {
  id: number;
  name: string;
  startIndex: number;
  endIndex: number;
  length: number; // meters
}

export interface DRSZone {
  id: string;
  detectionPoint: number; // track percentage
  activationPoint: number; // track percentage
  endPoint: number; // track percentage
}

export interface TrackConfig {
  name: string;
  country: string;
  totalLength: number; // meters
  sectors: Sector[];
  drsZones: DRSZone[];
  pitEntry: Position;
  pitExit: Position;
  startLine: Position;
  trackPoints: TrackPoint[]; // All points that define the racing line
}

// ---------------------------------------------------------------------------
// Weather Types
// ---------------------------------------------------------------------------

export type WeatherCondition = 'dry' | 'damp' | 'wet' | 'heavy_rain';

export interface WeatherZone {
  sectorId: number;
  condition: WeatherCondition;
  temperature: number; // Celsius
  trackTemp: number; // Celsius
  humidity: number; // percentage
  windSpeed: number; // km/h
  windDirection: number; // degrees
  rainIntensity: number; // 0-100
  gripLevel: number; // 0-100
}

export interface WeatherAlert {
  id: string;
  severity: 'info' | 'warning' | 'danger';
  message: string;
  affectedSectors: number[];
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Incident & Alert Types
// ---------------------------------------------------------------------------

export type FlagType = 'green' | 'yellow' | 'double_yellow' | 'red' | 'blue' | 'white';

export interface RaceFlag {
  type: FlagType;
  sector?: number;
  timestamp: number;
  active: boolean;
}

export type IncidentType = 'collision' | 'spin' | 'debris' | 'mechanical' | 'slowdown';

export interface Incident {
  id: string;
  type: IncidentType;
  carId: string;
  position: Position;
  sector: number;
  timestamp: number;
  severity: 'low' | 'medium' | 'high';
  description: string;
}

export interface Alert {
  id: string;
  type: 'slowdown' | 'weather' | 'pit_congestion' | 'incident' | 'strategy';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  carId?: string;
  sector?: number;
  timestamp: number;
  acknowledged: boolean;
}

// ---------------------------------------------------------------------------
// Pit Stop & Strategy Types
// ---------------------------------------------------------------------------

export interface PitStop {
  carId: string;
  lapNumber: number;
  duration: number; // milliseconds
  tireChange: {
    from: TireCompound;
    to: TireCompound;
  };
  timestamp: number;
}

export interface StrategyRecommendation {
  carId: string;
  recommendation: string;
  pitWindowStart: number; // lap number
  pitWindowEnd: number; // lap number
  recommendedTire: TireCompound;
  confidence: number; // 0-100
  reasoning: string[];
}

// ---------------------------------------------------------------------------
// Race Session Types
// ---------------------------------------------------------------------------

export type SessionType = 'practice' | 'qualifying' | 'sprint' | 'race';

export interface RaceSession {
  sessionId: string;
  sessionType: SessionType;
  trackConfig: TrackConfig;
  totalLaps: number;
  currentLap: number;
  sessionTime: number; // seconds elapsed
  sessionStatus: 'not_started' | 'in_progress' | 'paused' | 'finished';
  weather: WeatherZone[];
  flags: RaceFlag[];
}

export interface RaceState {
  session: RaceSession;
  cars: Map<string, CarTelemetry>;
  incidents: Incident[];
  alerts: Alert[];
  pitStops: PitStop[];
}

// ---------------------------------------------------------------------------
// WebSocket Message Types
// ---------------------------------------------------------------------------

export type MessageType = 
  | 'telemetry_update'
  | 'weather_update'
  | 'incident'
  | 'alert'
  | 'flag_change'
  | 'pit_stop'
  | 'session_update'
  | 'strategy_recommendation';

export interface WebSocketMessage<T = any> {
  type: MessageType;
  timestamp: number;
  data: T;
}

// ---------------------------------------------------------------------------
// Detection Module Interfaces (for extensibility)
// ---------------------------------------------------------------------------

export interface DetectionModule {
  name: string;
  enabled: boolean;
  process(cars: CarTelemetry[], session: RaceSession): Alert[];
}

export interface SlowdownDetectionConfig {
  speedThreshold: number; // percentage below average
  timeWindow: number; // milliseconds
  minimumSpeed: number; // km/h
}

export interface PitLaneCongestionConfig {
  maxCarsInPit: number;
  warningThreshold: number;
}

export interface WeatherChangeConfig {
  rainThreshold: number;
  gripChangeThreshold: number;
  alertLeadTime: number; // seconds
}

// ---------------------------------------------------------------------------
// HPC Integration Interface (prepared for future implementation)
// ---------------------------------------------------------------------------

export interface HPCSimulationRequest {
  sessionId: string;
  currentState: RaceState;
  scenarios: Scenario[];
  priority: 'low' | 'normal' | 'high';
}

export interface Scenario {
  id: string;
  description: string;
  parameters: {
    weatherChanges?: WeatherZone[];
    fuelStrategy?: Record<string, number>;
    tireStrategy?: Record<string, TireCompound>;
  };
}

export interface HPCSimulationResult {
  scenarioId: string;
  predictedOutcome: {
    finalPositions: Record<string, number>;
    lapTimes: Record<string, number[]>;
    fuelUsage: Record<string, number>;
  };
  confidence: number;
  computeTime: number;
}

