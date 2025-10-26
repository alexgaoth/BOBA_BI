# Boba BI Frontend-API Connection Troubleshooting Guide

## Current Setup Status

✅ **API Server**: Running on port 5000 with CORS enabled
✅ **Frontend Server**: Running on port 8000 (Python HTTP server)
✅ **Application Logic**: Works correctly when running boba_bi.py directly

## Issues Identified & Fixed

### 1. ❌ Container Port Forwarding Issue

**Problem**: You're running in a devcontainer/codespace environment. The browser runs on your local machine, but servers run inside the container. `localhost:5000` in the browser doesn't reach the container's port 5000.

**Solution Applied**: Updated `demo_frontend.html` to auto-detect the environment and use the correct API URL:

```javascript
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : `${window.location.protocol}//${window.location.hostname.replace('-8000', '-5000')}`;
```

This automatically handles:
- Local development: uses `http://localhost:5000`
- Codespaces/devcontainer: uses forwarded port URL

### 2. ❌ Path Issue: 404 on /BOBA_BI/demo_frontend.html

**Problem**: The Python HTTP server is running FROM `/workspaces/BOBA_BI`:
```bash
python3 -m http.server 8000
```

This serves files at root level, so:
- ✅ `http://localhost:8000/demo_frontend.html` - Works
- ❌ `http://localhost:8000/BOBA_BI/demo_frontend.html` - 404 (BOBA_BI is already the root)

**Solution**: Use the correct URL without the `/BOBA_BI/` prefix.

### 3. ✅ Enhanced Debugging

**Added console logging** to help troubleshoot:
- Logs the detected API URL
- Logs the current page location
- Logs request and response details
- Shows detailed error messages

## How to Test

### Step 1: Verify Servers Are Running

```bash
# Check running processes
ps aux | grep -E "http.server|api_server.py" | grep -v grep

# Expected output:
# - python3 -m http.server 8000
# - python3 api_server.py (may show 2 processes due to Flask debug mode)
```

### Step 2: Test API Server Directly

```bash
# Health check
curl http://localhost:5000/

# Expected output:
# {
#   "service": "Boba BI API",
#   "status": "running",
#   "version": "1.0.0",
#   "timestamp": "..."
# }

# Test CORS headers
curl -H "Origin: http://localhost:8000" -v http://localhost:5000/api/stats 2>&1 | grep Access-Control

# Expected: Access-Control-Allow-Origin: *
```

### Step 3: Access Frontend in Browser

**For Local Development:**
- ✅ `http://localhost:8000/demo_frontend.html`
- ❌ `http://localhost:8000/BOBA_BI/demo_frontend.html`

**For Codespaces/Devcontainer:**
1. Open the **PORTS** panel in VS Code
2. Find ports 5000 and 8000
3. Click the "Open in Browser" icon for port 8000
4. Add `/demo_frontend.html` to the URL

Expected forwarded URL format:
```
https://[workspace-name]-8000.preview.app.github.dev/demo_frontend.html
```

### Step 4: Check Browser Console

Open browser DevTools (F12) and check the Console tab for:
```
🔧 API URL: [detected URL]
🌐 Current location: [current page URL]
📡 Sending request to: [API endpoint]
📥 Response status: [HTTP status code]
```

## Common Issues & Solutions

### Issue: "Failed to connect to API server"

**Diagnosis:**
1. Open browser console (F12)
2. Look for the API URL being used
3. Check for CORS errors or network errors

**Solutions:**

**A. In Codespaces - Ports Not Public**
```bash
# Make ports public
# In VS Code: PORTS panel → Right-click port → Port Visibility → Public
```

**B. API Server Not Running**
```bash
# Start API server
python3 api_server.py
```

**C. CORS Issue (shouldn't happen, but if it does)**
```python
# In api_server.py, CORS is already enabled:
from flask_cors import CORS
CORS(app)  # Line 20
```

### Issue: Mixed Content (HTTPS → HTTP)

If your frontend is served over HTTPS but trying to connect to HTTP API:

**Solution**: Ensure API server is also accessible via HTTPS (Codespaces handles this automatically with port forwarding).

### Issue: Multiple API Server Instances

If you see multiple `api_server.py` processes, this is normal. Flask debug mode runs:
- Parent process
- Child process (auto-reloader)

To run without debug mode:
```python
# In api_server.py, change line 218:
app.run(host='0.0.0.0', port=5000, debug=False)
```

## Manual Testing Without Browser

Test the entire flow from command line:

```bash
# Generate schedule
curl -X POST http://localhost:5000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{"query": "How should I schedule employees for next week?"}'

# Download CSV
curl -X POST http://localhost:5000/api/schedule/download \
  -H "Content-Type: application/json" \
  -d '{"query": "Generate schedule"}' \
  -o schedule.csv
```

## Starting Fresh

If you want to restart everything:

```bash
# Kill all servers
pkill -f "http.server"
pkill -f "api_server.py"

# Start API server
python3 api_server.py &

# Start frontend server (in a new terminal)
python3 -m http.server 8000
```

## Environment Variables

If you're missing API keys, create a `.env` file:

```bash
# .env
ANTHROPIC_API_KEY=your_key_here
```

Then load it before running:
```bash
export $(cat .env | xargs)
python3 api_server.py
```

## Success Indicators

✅ API server shows: `🚀 Starting server on http://localhost:5000`
✅ Browser console shows: `🔧 API URL: http://localhost:5000`
✅ API request logs: `📡 Sending request to: http://localhost:5000/api/schedule`
✅ Schedule displays in the frontend with data

## Still Having Issues?

1. **Check the browser console** for detailed error messages
2. **Check the API server terminal** for incoming request logs
3. **Verify port forwarding** in VS Code PORTS panel
4. **Test API directly** with curl to isolate frontend vs backend issues

## Updated Files

- ✅ `demo_frontend.html` - Auto-detects API URL, enhanced debugging
- ✅ `api_server.py` - Already configured with CORS
- ✅ Added this troubleshooting guide
