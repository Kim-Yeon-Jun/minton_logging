#!/bin/bash

#chmod +x port-monitor.sh
#./port-monitor.sh
PORTS=(3000 7700 8000 8080 5432)

while true
do
    clear
    echo "=============================="
    echo "       PORT MONITOR"
    echo "=============================="
    date
    echo ""

    for PORT in "${PORTS[@]}"
    do
        RESULT=$(netstat -ano | grep ":$PORT ")

        if [ -z "$RESULT" ]; then
            echo "PORT $PORT : ❌ NOT USED"
        else
            PID=$(echo $RESULT | awk '{print $5}')
            echo "PORT $PORT : ✅ USED (PID: $PID)"
        fi
    done

    echo ""
    echo "Press Ctrl+C to stop"
    sleep 2
done