# 🚀 Step-by-Step Setup Instructions

This document provides detailed, copy-paste friendly commands to get the F1 Race Strategy Platform running.

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Node.js 20.x or higher installed (`node --version`)
- [ ] npm 9.x or higher installed (`npm --version`)
- [ ] Git installed (`git --version`)
- [ ] A terminal/command prompt
- [ ] A modern web browser (Chrome, Firefox, Edge, Safari)

## 🛠️ Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd nmc2
```

### Step 2: Install All Dependencies

**Option A: Install everything at once**
```bash
npm run install:all
```

**Option B: Install step by step**
```bash
# Root dependencies
npm install

# Shared types
cd shared
npm install
cd ..

# Backend dependencies
cd backend
npm install
cd ..

# Frontend dependencies
cd frontend
npm install
cd ..
```

### Step 3: Build Shared Types

```bash
cd shared
npm run build
cd ..
```

You should see:
```
> @f1-platform/shared@1.0.0 build
> tsc
```

### Step 4: Start the Backend Server

**Open Terminal 1:**
```bash
cd backend
npm run dev
```

You should see:
```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   F1 Race Strategy Platform - Backend Server                 ║
║                                                               ║
║   Server running on: http://localhost:3001                   ║
║   WebSocket endpoint: ws://localhost:3001                    ║
║                                                               ║
║   Ready to receive connections...                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Keep this terminal running!**

### Step 5: Start the Frontend

**Open Terminal 2 (new terminal window/tab):**
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.0.12  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Keep this terminal running too!**

### Step 6: Open in Browser

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the F1 Race Strategy Platform interface.

### Step 7: Start the Race!

1. Wait for "Connected" indicator in the top-right corner (green dot)
2. Click the green **"Start"** button
3. Watch the cars race around the track! 🏎️

## 🐳 Docker Alternative (Optional)

If you prefer using Docker:

### Prerequisites
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)

### Commands

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Then open: `http://localhost:5173`

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend server shows "Ready to receive connections"
- [ ] Frontend shows "Connected" with green indicator
- [ ] Clicking "Start" makes cars appear on track
- [ ] Cars are moving around the track
- [ ] Live Timing table shows driver information
- [ ] Weather conditions are displayed
- [ ] Clicking on a car shows its detailed telemetry

## 🎮 Quick Test

Run this sequence to verify full functionality:

1. **Start Session**: Click "Start" button
2. **Select Car**: Click on any moving car on the track
3. **View Telemetry**: Check the overlay showing speed, tire, fuel, etc.
4. **Check Dashboard**: Verify all dashboard cards are updating
5. **Toggle Weather**: Click "Weather: ON" to see weather overlay
6. **Stop Session**: Click "Stop" button
7. **Reset**: Click "Reset" button

If all steps work, you're ready to go! 🎉

## 🔧 Terminal Commands Reference

### Development Commands

```bash
# Start backend (from backend/)
npm run dev

# Start frontend (from frontend/)
npm run dev

# Build shared types (from shared/)
npm run build

# Build backend (from backend/)
npm run build

# Build frontend (from frontend/)
npm run build
```

### Session Control

- **Start Session**: Click "Start" button in UI, or:
  ```bash
  curl -X POST http://localhost:3001/api/session/start
  ```

- **Stop Session**: Click "Stop" button in UI, or:
  ```bash
  curl -X POST http://localhost:3001/api/session/stop
  ```

- **Reset Session**: Click "Reset" button in UI, or:
  ```bash
  curl -X POST http://localhost:3001/api/session/reset
  ```

### Testing API Endpoints

```bash
# Health check
curl http://localhost:3001/api/health

# Get track config
curl http://localhost:3001/api/track

# Get teams
curl http://localhost:3001/api/teams

# Get session info
curl http://localhost:3001/api/session
```

## 🚨 Common Issues & Solutions

### Issue: Port 3001 already in use

**Solution:**
```bash
# Find process using port 3001
# Windows:
netstat -ano | findstr :3001
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3001 | xargs kill -9
```

Or change the port in `backend/src/server.ts`:
```typescript
const PORT = process.env.PORT || 3002; // Change to 3002
```

And update frontend `vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:3002', // Match backend port
    changeOrigin: true
  }
}
```

### Issue: Frontend not connecting

**Check:**
1. Backend is running on port 3001
2. Browser console for errors (F12 → Console)
3. Network tab for WebSocket connection (F12 → Network → WS)

**Solution:**
```bash
# Restart backend
cd backend
npm run dev

# Clear browser cache and refresh
```

### Issue: Cars not appearing

**Solution:**
1. Click the "Start" button (top-right)
2. Check backend terminal for errors
3. Refresh browser page
4. Click "Reset" then "Start" again

### Issue: `npm run install:all` fails

**Solution:**
Run installations individually:
```bash
cd shared && npm install && cd ..
cd backend && npm install && cd ..
cd frontend && npm install && cd ..
```

### Issue: TypeScript errors

**Solution:**
```bash
# Rebuild shared types
cd shared
rm -rf dist node_modules
npm install
npm run build
cd ..

# Rebuild backend
cd backend
rm -rf dist node_modules
npm install
cd ..

# Rebuild frontend
cd frontend
rm -rf dist node_modules
npm install
cd ..
```

## 📊 Expected Behavior

### Backend Terminal Output
```
✅ Connected to WebSocket server
Starting race session...
Client connected: <socket-id>
```

### Frontend Browser Console
```
✅ Connected to WebSocket server
```

### Visual Indicators
- **Green dot**: Connected to backend
- **Cars moving**: Session is active
- **Dashboard updating**: Real-time data flowing
- **Alerts appearing**: Detection modules working

## 🎯 Next Steps

Once everything is running:

1. **Explore the UI**: Try all dashboard features
2. **Read the README**: Understand architecture and features
3. **Modify the Code**: Customize track, teams, or detection logic
4. **Add Features**: Implement new detection modules or visualizations
5. **Scale It**: Prepare for HPC integration

## 💡 Tips for Development

1. **Hot Reload**: Both frontend and backend support hot reload
2. **Browser DevTools**: Use F12 to inspect WebSocket messages
3. **Multiple Windows**: Open multiple browser tabs to test multi-user
4. **Terminal Logs**: Watch both terminals for debugging
5. **Git**: Commit frequently as you add features

## 📞 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review backend terminal logs
3. Check browser console (F12)
4. Verify all dependencies are installed
5. Try the Docker approach as alternative
6. Open an issue on GitHub

---

**Happy Racing! 🏁**

