#!/bin/bash

# 프론트엔드 서버 관리 스크립트 (Vite / Node.js)
PID_FILE="./frontend.pid"
LOG_FILE="./frontend.log"

# .env 파일에서 PORT 읽어오기 (기본값: 3000)
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi
PORT=${PORT:-3000}

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo ">>> 프론트엔드 개발 서버가 이미 실행 중입니다. (PID: $(cat $PID_FILE), Port: $PORT)"
    else
        echo ">>> 프론트엔드 개발 서버를 시작합니다... (Port: $PORT)"
        nohup npx vite --port "$PORT" > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo ">>> 프론트엔드 개발 서버가 시작되었습니다. (PID: $!, Port: $PORT)"
    fi
}

stop() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        PID=$(cat "$PID_FILE")
        echo ">>> 프론트엔드 개발 서버를 중지합니다... (PID: $PID)"
        kill "$PID"
        rm -f "$PID_FILE"
        echo ">>> 프론트엔드 개발 서버가 중지되었습니다."
    else
        echo ">>> 실행 중인 프론트엔드 개발 서버가 없습니다."
        rm -f "$PID_FILE"
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo ">>> 프론트엔드 개발 서버 상태: 실행 중 (PID: $(cat $PID_FILE), Port: $PORT)"
    else
        echo ">>> 프론트엔드 개발 서버 상태: 중지됨"
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
        echo ">>> 프론트엔드 개발 서버를 재시작합니다..."
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    logs)
        echo ">>> 실시간 프론트엔드 로그 확인 (종료하려면 Ctrl+C):"
        tail -f "$LOG_FILE"
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
