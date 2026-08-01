#!/bin/bash

# 백엔드 서버 관리 스크립트 (FastAPI / Uvicorn)
PID_FILE="./backend.pid"
LOG_FILE="./backend.log"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo ">>> 백엔드 서버가 이미 실행 중입니다. (PID: $(cat $PID_FILE))"
    else
        echo ">>> 백엔드 서버를 시작합니다..."
        # 가상환경 선택 (.venv/Scripts/python [Windows/Git Bash] 또는 .venv/bin/python [Linux/Mac])
        if [ -f ".venv/Scripts/python" ]; then
            PYTHON_EXEC=".venv/Scripts/python"
        elif [ -f ".venv/bin/python" ]; then
            PYTHON_EXEC=".venv/bin/python"
        else
            PYTHON_EXEC="python"
        fi

        nohup $PYTHON_EXEC main.py > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo ">>> 백엔드 서버가 시작되었습니다. (PID: $!)"
    fi
}

stop() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        PID=$(cat "$PID_FILE")
        echo ">>> 백엔드 서버를 중지합니다... (PID: $PID)"
        kill "$PID"
        rm -f "$PID_FILE"
        echo ">>> 백엔드 서버가 중지되었습니다."
    else
        echo ">>> 실행 중인 백엔드 서버가 없습니다."
        rm -f "$PID_FILE"
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo ">>> 백엔드 서버 상태: 실행 중 (PID: $(cat $PID_FILE))"
    else
        echo ">>> 백엔드 서버 상태: 중지됨"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        echo ">>> 백엔드 서버를 재시작합니다..."
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    logs)
        echo ">>> 실시간 백엔드 로그 확인 (종료하려면 Ctrl+C):"
        tail -f "$LOG_FILE"
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
