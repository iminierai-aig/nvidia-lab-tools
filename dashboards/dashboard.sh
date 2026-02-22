#!/bin/bash
# dashboard.sh - Combined GPU monitoring dashboard

clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              NVIDIA GPU MONITORING DASHBOARD                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

while true; do
    # Header
    tput cup 3 0  # Move cursor
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # GPU Summary
    echo "=== GPU Summary ==="
    nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader | \
    while IFS=',' read -r idx name temp util mem_used mem_total power; do
        printf "GPU %s: %s | Temp: %s | Util: %s | Mem: %s/%s | Power: %s\n" \
            "$idx" "$name" "$temp" "$util" "$mem_used" "$mem_total" "$power"
    done
    echo ""
    
    # Processes
    echo "=== Active Processes ==="
    nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv,noheader 2>/dev/null | head -5 || echo "No GPU processes"
    echo ""
    
    # Add padding
    echo ""
    echo "Press Ctrl+C to exit"
    
    sleep 2
done
