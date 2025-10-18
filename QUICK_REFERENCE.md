# ⚡ Quick Reference Guide

## 🚀 Getting Started (Copy-Paste)

### First Time Setup
```bash
# 1. Navigate to project
cd nmc2

# 2. Install everything
npm install
cd shared && npm install && npm run build && cd ..
cd backend && npm install && cd ..
cd frontend && npm install && cd ..

# Done! Now start the servers...
```

### Starting the Application

**Terminal 1 - Backend:**
```bash
cd backend
npm run dev
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Browser:**
```
http://localhost:5173
```

## 📁 Project Structure

```
nmc2/
├── frontend/              # React app
│   └── src/
│       ├── components/    # TrackVisualization, Dashboard
│       ├── services/      # socketService
│       └── App.tsx        # Main app
├── backend/              # Node.js server
│   └── src/
│       ├── config/        # trackData, teams
│       ├── services/      # Simulation, Detection
│       └── server.ts      # WebSocket server
└── shared/               # TypeScript types
    └── src/types.ts      # All interfaces
```

## 🎮 UI Controls

| Action | Button | Location |
|--------|--------|----------|
| Start Race | Green "Start" | Top-right header |
| Stop Race | Red "Stop" | Top-right header |
| Reset | "Reset" | Top-right header |
| Select Car | Click on car | Track canvas |
| Toggle Weather | "Weather" button | Track overlay |

## 🔌 API Endpoints

```bash
# Health Check
curl http://localhost:3001/api/health

# Get Track Configuration
curl http://localhost:3001/api/track

# Get Teams
curl http://localhost:3001/api/teams

# Get Session Info
curl http://localhost:3001/api/session

# Start Session
curl -X POST http://localhost:3001/api/session/start

# Stop Session
curl -X POST http://localhost:3001/api/session/stop

# Reset Session
curl -X POST http://localhost:3001/api/session/reset
```

## 📊 Key Files to Modify

### Add/Change Teams
```typescript
// backend/src/config/trackData.ts
export const TEAMS = [
  { id: 'NEW', name: 'New Team', color: '#FF0000' },
  // ...
];
```

### Add Driver Names
```typescript
// backend/src/config/trackData.ts
export const DRIVER_NAMES = [
  'New Driver',
  // ...
];
```

### Modify Track Layout
```typescript
// backend/src/config/trackData.ts
const generateTrackPoints = (): TrackPoint[] => {
  // Modify x,y coordinates
  points.push({ x: 300, y: 320, sector: 1 });
};
```

### Add Detection Module
```typescript
// backend/src/services/DetectionService.ts
private detectYourEvent(cars: CarTelemetry[]): Alert[] {
  // Your detection logic
  return alerts;
}

public processDetections(...): { alerts, incidents } {
  alerts.push(...this.detectYourEvent(cars));
}
```

### Customize UI Colors
```css
/* frontend/src/index.css */
:root {
  --bg-primary: #0a0e1a;
  --accent-blue: #3b82f6;
  /* Change colors here */
}
```

## 🐛 Troubleshooting Commands

### Port Already in Use
```bash
# Kill process on port 3001 (Backend)
# Mac/Linux:
lsof -ti:3001 | xargs kill -9

# Windows:
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

### Clear Everything and Restart
```bash
# Clean all
cd backend && rm -rf node_modules dist && cd ..
cd frontend && rm -rf node_modules dist && cd ..
cd shared && rm -rf node_modules dist && cd ..

# Reinstall
cd shared && npm install && npm run build && cd ..
cd backend && npm install && cd ..
cd frontend && npm install && cd ..
```

### Check Logs
```bash
# Backend logs
cd backend && npm run dev

# Frontend logs (browser)
# Press F12 → Console tab
```

## 📝 Common Tasks

### Change Update Frequency
```typescript
// backend/src/server.ts
const UPDATE_FREQUENCY = 50; // milliseconds (20Hz)
// Change to 100 for 10Hz, 25 for 40Hz, etc.
```

### Add New Dashboard Component
```typescript
// 1. Create component
// frontend/src/components/YourComponent.tsx
export const YourComponent = ({ data }) => {
  return <div>{/* Your UI */}</div>;
};

// 2. Add to Dashboard
// frontend/src/components/Dashboard.tsx
<YourComponent data={yourData} />
```

### Add New WebSocket Event
```typescript
// Backend - emit event
io.emit('your_event', {
  type: 'your_event',
  data: yourData
});

// Frontend - listen for event
socketService.onYourEvent((data) => {
  console.log('Received:', data);
});
```

## 🎨 Customization Examples

### Change Number of Cars
```typescript
// backend/src/config/trackData.ts
export const DRIVER_NAMES = [
  // Add or remove driver names
  // Number of names = number of cars
];
```

### Change Lap Count
```typescript
// backend/src/server.ts
const raceSession: RaceSession = {
  // ...
  totalLaps: 50, // Change this
};
```

### Modify Speed Range
```typescript
// backend/src/services/SimulationService.ts
private calculateSpeedForPosition(...): number {
  let targetSpeed: number;
  // Modify these ranges
  if (sector === 1) {
    targetSpeed = 320; // Max speed
  } else {
    targetSpeed = 160; // Min speed
  }
}
```

## 🔍 Debug Checklist

- [ ] Backend running on port 3001?
- [ ] Frontend running on port 5173?
- [ ] Browser console shows "Connected"?
- [ ] Green dot in top-right corner?
- [ ] Clicked "Start" button?
- [ ] No errors in terminal?
- [ ] WebSocket connected in Network tab?

## 📦 Build Commands

```bash
# Build everything
cd shared && npm run build && cd ..
cd backend && npm run build && cd ..
cd frontend && npm run build && cd ..

# Run production build
cd backend && npm start

# Preview frontend build
cd frontend && npm run preview
```

## 🐳 Docker Commands

```bash
# Start with Docker
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop
docker-compose down

# Rebuild
docker-compose up --build --force-recreate
```

## 🧪 Testing the Application

```bash
# 1. Start backend and frontend
# 2. Open http://localhost:5173
# 3. Click "Start"
# 4. Verify:
#    - Cars moving on track ✓
#    - Dashboard updating ✓
#    - Click on a car shows info ✓
#    - Weather conditions visible ✓
#    - Alerts appear in dashboard ✓
```

## 📚 Important Files

| File | Purpose |
|------|---------|
| `backend/src/server.ts` | Main server & WebSocket logic |
| `backend/src/services/SimulationService.ts` | Car simulation |
| `backend/src/services/DetectionService.ts` | Alert detection |
| `backend/src/config/trackData.ts` | Track & teams config |
| `frontend/src/App.tsx` | Main React app |
| `frontend/src/components/TrackVisualization.tsx` | Track canvas |
| `frontend/src/components/Dashboard.tsx` | Dashboard UI |
| `frontend/src/services/socketService.ts` | WebSocket client |
| `shared/src/types.ts` | All TypeScript types |

## 🎯 Feature Flags

Enable/disable features by modifying these:

```typescript
// Show weather overlay
const [showWeatherOverlay, setShowWeatherOverlay] = useState(true);

// Alert cooldown (ms)
private readonly ALERT_COOLDOWN = 5000;

// Telemetry update rate (ms)
const UPDATE_FREQUENCY = 50;

// Max cars displayed in timing table
.slice(0, 10) // Show top 10
```

## 💡 Performance Tips

1. **Reduce Update Frequency**: Change `UPDATE_FREQUENCY` to 100ms
2. **Limit Cars**: Reduce `DRIVER_NAMES` array size
3. **Disable Weather Overlay**: Toggle off in UI
4. **Reduce Alert History**: Change `.slice(0, 50)` to lower number
5. **Canvas Size**: Reduce canvas dimensions in component

## 🚨 Known Limitations

- **Simulation only**: Uses generated data, not real F1 telemetry
- **No persistence**: Data lost on refresh
- **No authentication**: Open to all connections
- **Local only**: Not configured for remote deployment
- **Browser dependent**: Best in Chrome/Edge

## 📞 Quick Support

**Problem**: Cars not moving
- **Solution**: Click "Start" button

**Problem**: Connection failed
- **Solution**: Restart backend, refresh browser

**Problem**: Port in use
- **Solution**: Kill process or change port

**Problem**: Build errors
- **Solution**: `rm -rf node_modules && npm install`

---

**Save this file for quick reference during development!**

