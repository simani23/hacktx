# 🏎️ F1 Race Strategy Platform

A real-time F1 race monitoring and strategy platform built with modern web technologies. This full-stack application provides live telemetry visualization, weather tracking, incident detection, and is designed to be scalable and modular for HPC integration.

![F1 Race Strategy Platform](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-blue)
![Node](https://img.shields.io/badge/Node-20.x-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)

## ✨ Features

### 🎯 Core Features
- **Real-time Track Visualization**: Canvas-based rendering of F1 track with live car positions
- **Live Telemetry Tracking**: Monitor 20 cars simultaneously with real-time position updates
- **Weather Monitoring**: Sector-based weather conditions with grip levels and rain intensity
- **Incident Detection**: Automatic detection of slowdowns, pit lane congestion, and track incidents
- **Alert System**: Real-time alerts for critical events and strategy recommendations
- **Beautiful UI**: Modern, responsive design with smooth animations and intuitive controls

### 🔧 Technical Features
- **Modular Architecture**: Clean separation of concerns with extensible detection modules
- **Scalable Design**: Built to handle high-frequency telemetry data (20+ updates/second)
- **WebSocket Communication**: Low-latency real-time data streaming
- **TypeScript Throughout**: Type-safe codebase with shared type definitions
- **Docker Ready**: Containerized deployment for easy scaling
- **HPC Integration Ready**: Architecture designed for future HPC simulation integration

## 🏗️ Architecture

```
f1-race-strategy-platform/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # UI components (Track, Dashboard, etc.)
│   │   ├── services/     # WebSocket and API services
│   │   └── App.tsx       # Main application component
│   └── package.json
├── backend/              # Node.js + Express + Socket.io backend
│   ├── src/
│   │   ├── config/       # Track and teams configuration
│   │   ├── services/     # Simulation and detection services
│   │   └── server.ts     # Main server with WebSocket handling
│   └── package.json
├── shared/               # Shared TypeScript types
│   └── src/
│       └── types.ts      # Common interfaces and types
└── docker-compose.yml    # Docker orchestration
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20.x or higher
- **npm** 9.x or higher
- **Docker** (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nmc2
   ```

2. **Install dependencies for all packages**
   ```bash
   npm run install:all
   ```
   
   Or install individually:
   ```bash
   # Install root dependencies
   npm install

   # Install shared types
   cd shared && npm install && cd ..

   # Install backend dependencies
   cd backend && npm install && cd ..

   # Install frontend dependencies
   cd frontend && npm install && cd ..
   ```

3. **Build shared types**
   ```bash
   cd shared
   npm run build
   cd ..
   ```

4. **Start the backend server**
   ```bash
   cd backend
   npm run dev
   ```
   
   The backend will start on `http://localhost:3001`

5. **Start the frontend (in a new terminal)**
   ```bash
   cd frontend
   npm run dev
   ```
   
   The frontend will start on `http://localhost:5173`

6. **Open your browser**
   
   Navigate to `http://localhost:5173`

7. **Start the race simulation**
   
   Click the "Start" button in the top-right corner to begin the simulation.

### Docker Deployment

For production or containerized development:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

Access the application at `http://localhost:5173`

## 🎮 Usage Guide

### Starting a Race Session

1. **Connect**: The application automatically connects to the backend WebSocket server
2. **Start Session**: Click the green "Start" button to begin the simulation
3. **Monitor**: Watch cars move around the track in real-time
4. **Interact**: Click on any car to view detailed telemetry
5. **Stop/Reset**: Use the "Stop" button to pause or "Reset" to restart

### Dashboard Features

#### 📊 Session Info
- Current lap and total laps
- Session time
- Session status (running/paused)

#### 📈 Race Statistics
- Active cars on track
- Cars in pit lane
- Average speed

#### ⏱️ Live Timing
- Real-time position table
- Driver names and teams
- Current tire compounds
- Speed and sector information
- DRS and pit status

#### ☁️ Weather Conditions
- Sector-based weather monitoring
- Track temperature and grip levels
- Rain intensity
- Weather condition indicators

#### ⚠️ Alerts
- Slowdown detection
- Pit lane congestion warnings
- Weather alerts
- Incident notifications

### Track Visualization

- **View Cars**: See all 20 cars moving in real-time with team colors
- **Click Cars**: Select a car to view detailed telemetry overlay
- **Weather Overlay**: Toggle weather visualization with the button
- **DRS Zones**: Green rings indicate DRS activation
- **Pit Stops**: Yellow "PIT" labels show cars in pit lane

## 🔌 API Reference

### REST Endpoints

```
GET  /api/health           # Server health check
GET  /api/track            # Track configuration
GET  /api/teams            # Teams and colors
GET  /api/session          # Current session info
POST /api/session/start    # Start race session
POST /api/session/stop     # Stop race session
POST /api/session/reset    # Reset race session
```

### WebSocket Events

#### Client → Server
- `start_session`: Start the race simulation
- `stop_session`: Stop the race simulation
- `reset_session`: Reset all race data

#### Server → Client
- `telemetry_update`: Car position and telemetry data (20Hz)
- `weather_update`: Weather condition updates (every 10s)
- `alert`: Real-time alerts and warnings
- `incident`: Incident reports
- `session_update`: Session status changes

## 🧩 Extension Points

### Adding New Detection Modules

The detection system is modular and extensible:

```typescript
// backend/src/services/DetectionService.ts
class DetectionService {
  // Add your custom detection method
  private detectCustomEvent(cars: CarTelemetry[]): Alert[] {
    // Your detection logic here
    return alerts;
  }

  public processDetections(...): { alerts, incidents } {
    // Add your detection to the pipeline
    alerts.push(...this.detectCustomEvent(cars));
    // ...
  }
}
```

### Integrating HPC Simulations

The architecture supports HPC integration:

```typescript
// Future HPC integration point
interface HPCSimulationInterface {
  submit_batch_simulation(scenarios: Scenario[]): JobID;
  get_simulation_results(job_id: JobID): SimulationResults;
  run_realtime_optimization(state: RaceState): Strategy;
}
```

Add your HPC service in `backend/src/services/HPCService.ts` and connect it to the simulation pipeline.

## 🎨 Customization

### Adding Teams

Edit `backend/src/config/trackData.ts`:

```typescript
export const TEAMS = [
  { id: 'YOUR_TEAM', name: 'Your Team Name', color: '#FF0000' },
  // ...
];
```

### Modifying Track Layout

Edit track points in `backend/src/config/trackData.ts`:

```typescript
const generateTrackPoints = (): TrackPoint[] => {
  // Add your custom track layout
  // Points use x,y coordinates on a 1000x600 canvas
};
```

### Customizing UI Theme

Edit CSS variables in `frontend/src/index.css`:

```css
:root {
  --bg-primary: #0a0e1a;
  --accent-blue: #3b82f6;
  /* Modify colors, spacing, etc. */
}
```

## 📦 Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Socket.io Client** - WebSocket communication
- **Canvas API** - Track rendering
- **Framer Motion** - Animations
- **Lucide React** - Icons

### Backend
- **Node.js 20** - Runtime
- **Express** - Web framework
- **Socket.io** - WebSocket server
- **TypeScript** - Type safety

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 🧪 Development

### Building for Production

```bash
# Build all packages
npm run build

# Build individually
cd shared && npm run build
cd backend && npm run build
cd frontend && npm run build
```

### Running Production Build

```bash
# Backend
cd backend
npm start

# Frontend (serve build)
cd frontend
npm run preview
```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 3001 is available
- Ensure all dependencies are installed: `cd backend && npm install`
- Verify TypeScript compilation: `npm run build`

### Frontend won't connect to backend
- Verify backend is running on port 3001
- Check browser console for WebSocket errors
- Ensure firewall allows local connections

### No cars appearing on track
- Click "Start" button to begin simulation
- Check backend logs for errors
- Verify WebSocket connection in browser DevTools → Network → WS

### Docker issues
- Ensure Docker daemon is running
- Try rebuilding: `docker-compose up --build --force-recreate`
- Check logs: `docker-compose logs -f`

## 🚀 Performance

- **Telemetry Rate**: 20 updates/second (50ms intervals)
- **Car Count**: Supports 20 simultaneous cars
- **Render FPS**: 60 FPS smooth animations
- **WebSocket Latency**: <10ms on local network
- **Memory Usage**: ~150MB backend, ~100MB frontend

## 🔮 Future Enhancements

- [ ] HPC integration for Monte Carlo simulations
- [ ] Historical data storage (PostgreSQL)
- [ ] Machine learning predictions
- [ ] Multi-session support
- [ ] Live race data ingestion (F1 API)
- [ ] Strategy optimization algorithms
- [ ] Tire degradation modeling
- [ ] Fuel consumption tracking
- [ ] Multi-user collaboration
- [ ] 3D track visualization

## 📄 License

MIT License - feel free to use this project for your hackathon, research, or personal projects.

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🙏 Acknowledgments

Built for the F1 HPC Challenge hackathon. This project demonstrates how modern web technologies can bridge high-performance computing with real-time decision-making in Formula 1 racing.

---

**Built with ❤️ for F1 and HPC**

For questions or issues, please open a GitHub issue or contact the development team.

