import React from 'react';
import { CarTelemetry, WeatherZone, Alert, RaceSession } from '../../../shared/src/types';
import { Timer, Gauge, Cloud, AlertTriangle, Flag, Users } from 'lucide-react';
import './Dashboard.css';

interface DashboardProps {
  session: RaceSession | null;
  cars: CarTelemetry[];
  weather: WeatherZone[];
  alerts: Alert[];
  teams: Array<{ id: string; name: string; color: string }>;
}

/**
 * Dashboard Component - Displays race statistics and information
 */
export const Dashboard: React.FC<DashboardProps> = ({
  session,
  cars,
  weather,
  alerts,
  teams
}) => {
  // Calculate statistics
  const activeCars = cars.filter(c => !c.inPit).length;
  const carsInPit = cars.filter(c => c.inPit).length;
  const averageSpeed = cars.length > 0
    ? Math.round(cars.reduce((sum, car) => sum + car.speed, 0) / cars.length)
    : 0;

  // Format time
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Get weather condition emoji
  const getWeatherEmoji = (condition: string): string => {
    switch (condition) {
      case 'dry': return '☀️';
      case 'damp': return '🌤️';
      case 'wet': return '🌧️';
      case 'heavy_rain': return '⛈️';
      default: return '☁️';
    }
  };

  return (
    <div className="dashboard">
      {/* Session Info */}
      <div className="dashboard-card">
        <div className="card-header">
          <Flag size={20} />
          <h3>Session Info</h3>
        </div>
        <div className="card-content">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Status</span>
              <span className={`badge badge-${session?.sessionStatus === 'in_progress' ? 'success' : 'info'}`}>
                {session?.sessionStatus.replace('_', ' ').toUpperCase() || 'NOT STARTED'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Lap</span>
              <span className="info-value">
                {session?.currentLap || 0} / {session?.totalLaps || 0}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Session Time</span>
              <span className="info-value">
                {formatTime(session?.sessionTime || 0)}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Track</span>
              <span className="info-value">{session?.trackConfig.name || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Race Statistics */}
      <div className="dashboard-card">
        <div className="card-header">
          <Gauge size={20} />
          <h3>Race Statistics</h3>
        </div>
        <div className="card-content">
          <div className="stats-grid">
            <div className="stat-box">
              <div className="stat-icon" style={{ background: 'var(--accent-green)' }}>
                <Users size={24} />
              </div>
              <div className="stat-info">
                <span className="stat-value">{activeCars}</span>
                <span className="stat-label">Active Cars</span>
              </div>
            </div>
            <div className="stat-box">
              <div className="stat-icon" style={{ background: 'var(--accent-yellow)' }}>
                <Flag size={24} />
              </div>
              <div className="stat-info">
                <span className="stat-value">{carsInPit}</span>
                <span className="stat-label">In Pit Lane</span>
              </div>
            </div>
            <div className="stat-box">
              <div className="stat-icon" style={{ background: 'var(--accent-blue)' }}>
                <Gauge size={24} />
              </div>
              <div className="stat-info">
                <span className="stat-value">{averageSpeed}</span>
                <span className="stat-label">Avg Speed (km/h)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Live Timing */}
      <div className="dashboard-card timing-card">
        <div className="card-header">
          <Timer size={20} />
          <h3>Live Timing</h3>
        </div>
        <div className="card-content">
          <div className="timing-table-wrapper">
            <table className="timing-table">
              <thead>
                <tr>
                  <th>Pos</th>
                  <th>Driver</th>
                  <th>Team</th>
                  <th>Lap</th>
                  <th>Sector</th>
                  <th>Tire</th>
                  <th>Speed</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {cars
                  .sort((a, b) => b.currentLap - a.currentLap || b.speed - a.speed)
                  .slice(0, 10)
                  .map((car, index) => {
                    const team = teams.find(t => t.id === car.teamId);
                    return (
                      <tr key={car.id}>
                        <td className="position">{index + 1}</td>
                        <td className="driver-name">{car.driverName}</td>
                        <td>
                          <span
                            className="team-indicator"
                            style={{ backgroundColor: team?.color }}
                          />
                          {team?.id}
                        </td>
                        <td>{car.currentLap}</td>
                        <td className="sector">S{car.sector}</td>
                        <td>
                          <span className={`tire-badge tire-${car.tire}`}>
                            {car.tire[0].toUpperCase()}
                          </span>
                        </td>
                        <td>{car.speed} km/h</td>
                        <td>
                          {car.inPit && <span className="badge badge-warning">PIT</span>}
                          {car.drsEnabled && <span className="badge badge-success">DRS</span>}
                          {!car.inPit && !car.drsEnabled && <span className="text-muted">—</span>}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Weather Conditions */}
      <div className="dashboard-card">
        <div className="card-header">
          <Cloud size={20} />
          <h3>Weather Conditions</h3>
        </div>
        <div className="card-content">
          <div className="weather-grid">
            {weather.map(zone => (
              <div key={zone.sectorId} className="weather-zone">
                <div className="weather-header">
                  <span className="weather-emoji">{getWeatherEmoji(zone.condition)}</span>
                  <span className="sector-label">Sector {zone.sectorId}</span>
                </div>
                <div className="weather-details">
                  <div className="weather-stat">
                    <span className="label">Condition</span>
                    <span className="value">{zone.condition.replace('_', ' ')}</span>
                  </div>
                  <div className="weather-stat">
                    <span className="label">Grip</span>
                    <span className={`value ${zone.gripLevel < 70 ? 'text-warning' : ''}`}>
                      {zone.gripLevel}%
                    </span>
                  </div>
                  <div className="weather-stat">
                    <span className="label">Track Temp</span>
                    <span className="value">{Math.round(zone.trackTemp)}°C</span>
                  </div>
                  <div className="weather-stat">
                    <span className="label">Rain</span>
                    <span className="value">{zone.rainIntensity}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts */}
      <div className="dashboard-card alerts-card">
        <div className="card-header">
          <AlertTriangle size={20} />
          <h3>Alerts</h3>
          {alerts.length > 0 && (
            <span className="alert-count">{alerts.length}</span>
          )}
        </div>
        <div className="card-content">
          {alerts.length === 0 ? (
            <div className="no-alerts">
              <AlertTriangle size={32} opacity={0.3} />
              <p>No active alerts</p>
            </div>
          ) : (
            <div className="alerts-list">
              {alerts.slice(0, 5).map(alert => (
                <div key={alert.id} className={`alert-item alert-${alert.severity}`}>
                  <div className="alert-icon">
                    <AlertTriangle size={16} />
                  </div>
                  <div className="alert-content">
                    <span className="alert-message">{alert.message}</span>
                    <span className="alert-time">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
              {alerts.length > 5 && (
                <div className="alerts-more">
                  +{alerts.length - 5} more alerts
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

