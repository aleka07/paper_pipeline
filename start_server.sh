#!/bin/bash
# Paper Pipeline Server Startup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/server_${TIMESTAMP}.log"
PID_FILE="$LOG_DIR/server.pid"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Activate conda environment
source ~/miniforge3/etc/profile.d/conda.sh
conda activate paper-pipeline

case "${1:-start}" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "Server already running (PID: $(cat "$PID_FILE"))"
            exit 1
        fi
        
        echo "Starting Paper Pipeline server..."
        cd "$SCRIPT_DIR/backend"
        nohup python app.py > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Server started (PID: $(cat "$PID_FILE"))"
        echo "Logs: $LOG_FILE"
        echo "Access: http://localhost:5000"
        ;;
    
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "Stopping server (PID: $PID)..."
                kill "$PID"
                rm -f "$PID_FILE"
                echo "Server stopped."
            else
                echo "Server not running (stale PID file removed)."
                rm -f "$PID_FILE"
            fi
        else
            echo "No PID file found. Server not running."
        fi
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "Server running (PID: $(cat "$PID_FILE"))"
        else
            echo "Server not running."
        fi
        ;;
    
    logs)
        tail -f "$LOG_FILE"
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
