#!/bin/bash
PORT=8501
LOG_FILE="/tmp/cloudflared_neurostudy.log"
URL_FILE="/Users/dimaswastu/study-demo-env/data/active_public_url.txt"

echo "⚡ Menghentikan tunnel lama..."
pkill -f "cloudflared tunnel.*8501" 2>/dev/null
sleep 1

echo "🚀 Menyalakan Cloudflare Tunnel HTTP/2 ke 127.0.0.1:$PORT..."
cloudflared tunnel --protocol http2 --url "http://127.0.0.1:$PORT" > "$LOG_FILE" 2>&1 &

echo "⏳ Menunggu alokasi URL publik..."
for i in {1..20}; do
    URL=$(grep -oE "https://[a-zA-Z0-9-]+\.trycloudflare\.com" "$LOG_FILE" | head -n 1)
    if [ -n "$URL" ]; then
        echo "$URL" > "$URL_FILE"
        echo "═══════════════════════════════════════════════════════════════════════"
        echo "🎉 NEUROSTUDY AKTIF SECARA PUBLIK!"
        echo "🌐 URL: $URL"
        echo "═══════════════════════════════════════════════════════════════════════"
        exit 0
    fi
    sleep 1
done

echo "⚠️ Periksa log di $LOG_FILE"
