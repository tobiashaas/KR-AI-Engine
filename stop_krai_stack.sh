#!/bin/bash

# KRAI Engine - Stack Shutdown Script

echo "🛑 Stopping KRAI Engine Stack..."
echo "=================================="

# Stop all services gracefully
docker-compose down

echo ""
echo "🧹 Cleanup Options:"
echo "   ├─ Keep data volumes:     Already done ✅"
echo "   ├─ Remove volumes:        docker-compose down -v"
echo "   ├─ Remove images:         docker-compose down --rmi all"
echo "   └─ Full cleanup:          docker-compose down -v --rmi all --remove-orphans"

echo ""
echo "✅ KRAI Engine Stack stopped successfully!"
