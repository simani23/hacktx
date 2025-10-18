import React, { useEffect, useRef, useState } from 'react';
import { CarTelemetry, TrackConfig, TrackPoint, WeatherZone } from '../../../shared/src/types';
import './TrackVisualization.css';

interface TrackVisualizationProps {
  trackConfig: TrackConfig;
  cars: CarTelemetry[];
  weather: WeatherZone[];
  teams: Array<{ id: string; name: string; color: string }>;
}

/**
 * Track Visualization Component
 * Renders the F1 track and cars in real-time using Canvas
 */
export const TrackVisualization: React.FC<TrackVisualizationProps> = ({
  trackConfig,
  cars,
  weather,
  teams
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1000, height: 700 });
  const [selectedCar, setSelectedCar] = useState<string | null>(null);
  const [showWeatherOverlay, setShowWeatherOverlay] = useState(true);
  const animationFrameRef = useRef<number>();

  // Handle canvas resizing
  useEffect(() => {
    const updateDimensions = () => {
      const container = canvasRef.current?.parentElement;
      if (container) {
        const width = container.clientWidth;
        const height = Math.min(width * 0.7, 700); // Increased from 0.6 to 0.7
        setDimensions({ width, height });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Main rendering loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const render = () => {
      // Clear canvas
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);

      // Draw weather overlay
      if (showWeatherOverlay) {
        drawWeatherOverlay(ctx, weather);
      }

      // Draw track
      drawTrack(ctx, trackConfig.trackPoints);

      // Draw sector labels
      drawSectorLabels(ctx, trackConfig.sectors);

      // Draw cars
      cars.forEach(car => {
        const team = teams.find(t => t.id === car.teamId);
        drawCar(ctx, car, team?.color || '#ffffff', car.id === selectedCar);
      });

      // Draw start/finish line
      drawStartFinishLine(ctx, trackConfig.startLine);

      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [trackConfig, cars, weather, teams, selectedCar, showWeatherOverlay, dimensions]);

  /**
   * Draw the racing track
   */
  const drawTrack = (ctx: CanvasRenderingContext2D, points: TrackPoint[]) => {
    if (points.length === 0) return;

    const scaleX = dimensions.width / 1000;
    const scaleY = dimensions.height / 700; // Updated to match new canvas height

    // Draw track outline (outer)
    ctx.beginPath();
    ctx.strokeStyle = '#4b5563';
    ctx.lineWidth = 44;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    points.forEach((point, index) => {
      const x = point.x * scaleX;
      const y = point.y * scaleY;
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.closePath();
    ctx.stroke();

    // Draw track surface (inner)
    ctx.beginPath();
    ctx.strokeStyle = '#1f2937';
    ctx.lineWidth = 40;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    points.forEach((point, index) => {
      const x = point.x * scaleX;
      const y = point.y * scaleY;
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.closePath();
    ctx.stroke();

    // Draw racing line
    ctx.beginPath();
    ctx.strokeStyle = '#6b7280';
    ctx.lineWidth = 2;
    ctx.setLineDash([10, 10]);

    points.forEach((point, index) => {
      const x = point.x * scaleX;
      const y = point.y * scaleY;
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.closePath();
    ctx.stroke();
    ctx.setLineDash([]);
  };

  /**
   * Draw weather overlay
   */
  const drawWeatherOverlay = (ctx: CanvasRenderingContext2D, weatherZones: WeatherZone[]) => {
    const scaleX = dimensions.width / 1000;
    const scaleY = dimensions.height / 700; // Updated to match new canvas height

    weatherZones.forEach(zone => {
      if (zone.condition === 'dry') return;

      const sector = trackConfig.sectors.find(s => s.id === zone.sectorId);
      if (!sector) return;

      const startPoint = trackConfig.trackPoints[sector.startIndex];
      const endPoint = trackConfig.trackPoints[sector.endIndex];

      if (!startPoint || !endPoint) return;

      // Calculate sector bounds
      const sectorPoints = trackConfig.trackPoints.slice(sector.startIndex, sector.endIndex + 1);
      
      let minX = Infinity, maxX = -Infinity;
      let minY = Infinity, maxY = -Infinity;
      
      sectorPoints.forEach(point => {
        minX = Math.min(minX, point.x);
        maxX = Math.max(maxX, point.x);
        minY = Math.min(minY, point.y);
        maxY = Math.max(maxY, point.y);
      });

      // Draw weather effect
      const gradient = ctx.createRadialGradient(
        ((minX + maxX) / 2) * scaleX,
        ((minY + maxY) / 2) * scaleY,
        0,
        ((minX + maxX) / 2) * scaleX,
        ((minY + maxY) / 2) * scaleY,
        Math.max(maxX - minX, maxY - minY) * scaleX
      );

      if (zone.condition === 'wet' || zone.condition === 'heavy_rain') {
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');
      } else if (zone.condition === 'damp') {
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.15)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');
      }

      ctx.fillStyle = gradient;
      ctx.fillRect(
        minX * scaleX - 20,
        minY * scaleY - 20,
        (maxX - minX) * scaleX + 40,
        (maxY - minY) * scaleY + 40
      );
    });
  };

  /**
   * Draw sector labels
   */
  const drawSectorLabels = (ctx: CanvasRenderingContext2D, sectors: any[]) => {
    const scaleX = dimensions.width / 1000;
    const scaleY = dimensions.height / 700; // Updated to match new canvas height

    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    sectors.forEach(sector => {
      const midIndex = Math.floor((sector.startIndex + sector.endIndex) / 2);
      const point = trackConfig.trackPoints[midIndex];
      
      if (!point) return;

      // Draw label background
      const x = point.x * scaleX;
      const y = point.y * scaleY - 40;

      ctx.fillStyle = 'rgba(17, 24, 39, 0.9)';
      ctx.fillRect(x - 50, y - 15, 100, 30);

      // Draw label text
      ctx.fillStyle = '#9ca3af';
      ctx.fillText(sector.name, x, y);
    });
  };

  /**
   * Draw start/finish line
   */
  const drawStartFinishLine = (ctx: CanvasRenderingContext2D, position: { x: number; y: number }) => {
    const scaleX = dimensions.width / 1000;
    const scaleY = dimensions.height / 700; // Updated to match new canvas height
    const x = position.x * scaleX;
    const y = position.y * scaleY;

    // Draw checkered pattern
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(-Math.PI / 2);

    const squareSize = 8;
    for (let i = -2; i < 3; i++) {
      for (let j = 0; j < 2; j++) {
        const isWhite = (i + j) % 2 === 0;
        ctx.fillStyle = isWhite ? '#ffffff' : '#000000';
        ctx.fillRect(i * squareSize, j * squareSize, squareSize, squareSize);
      }
    }

    ctx.restore();
  };

  /**
   * Draw individual car
   */
  const drawCar = (
    ctx: CanvasRenderingContext2D,
    car: CarTelemetry,
    color: string,
    isSelected: boolean
  ) => {
    const scaleX = dimensions.width / 1000;
    const scaleY = dimensions.height / 700; // Updated to match new canvas height
    const x = car.position.x * scaleX;
    const y = car.position.y * scaleY;

    // Draw car glow if selected
    if (isSelected) {
      ctx.save();
      ctx.shadowColor = color;
      ctx.shadowBlur = 20;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 12, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // Draw car body
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fill();

    // Draw car outline
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.stroke();

    // Draw DRS indicator
    if (car.drsEnabled) {
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, 9, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Draw in-pit indicator
    if (car.inPit) {
      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('PIT', x, y - 15);
    }
  };

  /**
   * Handle car click
   */
  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const clickY = event.clientY - rect.top;

    const scaleX = dimensions.width / 1000;
    const scaleY = dimensions.height / 700; // Updated to match new canvas height

    // Find clicked car
    for (const car of cars) {
      const carX = car.position.x * scaleX;
      const carY = car.position.y * scaleY;
      const distance = Math.sqrt((clickX - carX) ** 2 + (clickY - carY) ** 2);

      if (distance < 15) {
        setSelectedCar(selectedCar === car.id ? null : car.id);
        return;
      }
    }

    setSelectedCar(null);
  };

  return (
    <div className="track-visualization">
      <div className="track-controls">
        <button
          className={`btn-secondary ${showWeatherOverlay ? 'active' : ''}`}
          onClick={() => setShowWeatherOverlay(!showWeatherOverlay)}
        >
          {showWeatherOverlay ? '☔ Weather: ON' : '☔ Weather: OFF'}
        </button>
      </div>
      
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        onClick={handleCanvasClick}
        className="track-canvas"
      />

      {selectedCar && (
        <div className="car-info-overlay">
          {(() => {
            const car = cars.find(c => c.id === selectedCar);
            if (!car) return null;
            const team = teams.find(t => t.id === car.teamId);
            
            return (
              <div className="car-info-card fade-in">
                <div className="car-info-header" style={{ borderLeftColor: team?.color }}>
                  <h3>{car.driverName}</h3>
                  <span className="team-name">{team?.name}</span>
                </div>
                <div className="car-info-stats">
                  <div className="stat">
                    <span className="stat-label">Speed</span>
                    <span className="stat-value">{car.speed} km/h</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Sector</span>
                    <span className="stat-value">{car.sector}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Tire</span>
                    <span className="stat-value">{car.tire.toUpperCase()}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Fuel</span>
                    <span className="stat-value">{car.fuel.toFixed(1)}%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Lap</span>
                    <span className="stat-value">{car.currentLap}</span>
                  </div>
                  {car.drsEnabled && (
                    <div className="stat">
                      <span className="badge badge-success">DRS ACTIVE</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};

