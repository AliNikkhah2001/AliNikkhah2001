#!/usr/bin/env bash
# Start Career Dashboard (API + Web)

set -euo pipefail

DASHBOARD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_PORT=8000
WEB_PORT=3000

echo "🚀 Starting Career Dashboard..."

# Check if database exists, import if needed
if [[ ! -f "$DASHBOARD_ROOT/career_db.json" ]]; then
    echo "📥 Importing cv.yaml..."
    cd "$DASHBOARD_ROOT"
    python3 scripts/import_cv.py
fi

# Kill any existing processes on our ports
lsof -ti:$API_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$WEB_PORT | xargs kill -9 2>/dev/null || true

# Start API
echo "🔧 Starting API on port $API_PORT..."
cd "$DASHBOARD_ROOT/api"
nohup python3 -m uvicorn main:app --host 127.0.0.1 --port $API_PORT > /tmp/career-api.log 2>&1 &
API_PID=$!
sleep 2

# Verify API is up
if curl -sf "http://127.0.0.1:$API_PORT/api/health" > /dev/null; then
    echo "✅ API running at http://127.0.0.1:$API_PORT"
else
    echo "❌ API failed to start. Check /tmp/career-api.log"
    exit 1
fi

# Start Web
echo "🌐 Starting Web on port $WEB_PORT..."
cd "$DASHBOARD_ROOT/web"
nohup npm run dev > /tmp/career-web.log 2>&1 &
WEB_PID=$!
sleep 3

# Verify Web is up
if curl -sf "http://127.0.0.1:$WEB_PORT" > /dev/null; then
    echo "✅ Web running at http://127.0.0.1:$WEB_PORT"
else
    echo "❌ Web failed to start. Check /tmp/career-web.log"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Career Dashboard is ready!"
echo ""
echo "📊 Dashboard:  http://127.0.0.1:$WEB_PORT"
echo "🔧 API:        http://127.0.0.1:$API_PORT"
echo "📖 API Docs:   http://127.0.0.1:$API_PORT/docs"
echo ""
echo "Tabs available:"
echo "  📅 Timeline       - Visual career timeline"
echo "  🧠 Knowledge Base - Edit positions, achievements, skills"
echo "  📄 CV Variants    - Compose targeted resume variants"
echo "  🚀 Publishing     - Export to GitHub, RenderCV, JSON Resume, LinkedIn"
echo "  💼 LinkedIn Export- Copy-paste formatted sections"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Wait for interrupt
trap "kill $API_PID $WEB_PID 2>/dev/null; echo 'Stopped.'" INT TERM
wait