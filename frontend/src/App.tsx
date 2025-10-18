import React, { useEffect, useState } from 'react';
import { TrackVisualization } from './components/TrackVisualization';
import { Dashboard } from './components/Dashboard';
import { socketService } from './services/socketService';
import {
  CarTelemetry,
  WeatherZone,
  Alert,
  RaceSession,
  TrackConfig
} from '../../shared/src/types';
import { Play, Pause, RotateCcw, Activity } from 'lucide-react';
import './App.css';

function App() {
  // State
  const [connected, setConnected] = useState(false);
  const [session, setSession] = useState<RaceSession | null>(null);
  const [trackConfig, setTrackConfig] = useState<TrackConfig | null>(null);
  const [cars, setCars] = useState<CarTelemetry[]>([]);
  const [weather, setWeather] = useState<WeatherZone[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [teams, setTeams] = useState<Array<{ id: string; name: string; color: string }>>([]);

  // Connect to WebSocket on mount
  useEffect(() => {
    const connectToServer = async () => {
      try {
        await socketService.connect();
        setConnected(true);

        // Fetch initial data
        fetchTeams();

        // Set up listeners
        socketService.onSessionUpdate((data) => {
          setSession(data);
          if (data.trackConfig) {
            setTrackConfig(data.trackConfig);
          }
          if (data.weather) {
            setWeather(data.weather);
          }
        });

        socketService.onTelemetryUpdate((data) => {
          setCars(data);
        });

        socketService.onWeatherUpdate((data) => {
          setWeather(data);
        });

        socketService.onAlert((alert) => {
          setAlerts((prev) => [alert, ...prev].slice(0, 50)); // Keep last 50 alerts
        });

      } catch (error) {
        console.error('Failed to connect to server:', error);
        setConnected(false);
      }
    };

    connectToServer();

    return () => {
      socketService.disconnect();
    };
  }, []);

  // Fetch teams from API
  const fetchTeams = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/teams');
      const data = await response.json();
      setTeams(data);
    } catch (error) {
      console.error('Failed to fetch teams:', error);
    }
  };

  // Session controls
  const handleStartSession = () => {
    socketService.startSession();
  };

  const handleStopSession = () => {
    socketService.stopSession();
  };

  const handleResetSession = () => {
    socketService.resetSession();
    setCars([]);
    setAlerts([]);
  };

  const isSessionActive = session?.sessionStatus === 'in_progress';

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">
              <Activity size={32} />
            </div>
            <div className="header-text">
              <h1>F1 Race Strategy Platform</h1>
              <p>Real-time Race Monitoring & HPC Integration</p>
            </div>
          </div>

          <div className="header-right">
            <div className="connection-status">
              <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`} />
              <span>{connected ? 'Connected' : 'Disconnected'}</span>
            </div>

            <div className="session-controls">
              <button
                onClick={handleStartSession}
                disabled={isSessionActive || !connected}
                className="btn-success"
                title="Start Session"
              >
                <Play size={16} />
                Start
              </button>
              <button
                onClick={handleStopSession}
                disabled={!isSessionActive}
                className="btn-danger"
                title="Stop Session"
              >
                <Pause size={16} />
                Stop
              </button>
              <button
                onClick={handleResetSession}
                disabled={isSessionActive}
                className="btn-secondary"
                title="Reset Session"
              >
                <RotateCcw size={16} />
                Reset
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {!connected ? (
          <div className="connection-message">
            <Activity size={64} className="pulse" />
            <h2>Connecting to server...</h2>
            <p>Please make sure the backend server is running on port 3001</p>
          </div>
        ) : !trackConfig ? (
          <div className="connection-message">
            <Activity size={64} className="pulse" />
            <h2>Loading track data...</h2>
          </div>
        ) : (
          <>
            {/* Track Visualization */}
            <section className="track-section">
              <TrackVisualization
                trackConfig={trackConfig}
                cars={cars}
                weather={weather}
                teams={teams}
              />
            </section>

            {/* Dashboard */}
            <section className="dashboard-section">
              <Dashboard
                session={session}
                cars={cars}
                weather={weather}
                alerts={alerts}
                teams={teams}
              />
            </section>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Built for F1 HPC Challenge • Scalable & Modular Architecture • Real-time Telemetry
        </p>
        <p className="text-muted">
          {cars.length} cars tracked • {alerts.length} active alerts
        </p>
      </footer>
    </div>
  );
}

export default App;

