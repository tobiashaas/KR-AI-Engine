# 🛑 KR-AI-Engine - Consolidated Stack Shutdown (PowerShell)
# Stoppt alle Services der konsolidierten Docker-Compose-Datei

param(
    [switch]$RemoveVolumes
)

Write-Host "🛑 Stopping KR-AI-Engine Consolidated Stack..." -ForegroundColor Red
Write-Host "===============================================" -ForegroundColor Red

# Stop the consolidated stack
if ($RemoveVolumes) {
    Write-Host "🧹 Stopping and removing volumes..." -ForegroundColor Yellow
    docker-compose down -v
} else {
    Write-Host "🧹 Stopping containers..." -ForegroundColor Yellow
    docker-compose down
}

Write-Host ""
Write-Host "🧹 Cleaning up containers and networks..." -ForegroundColor Yellow

# Remove orphaned containers
docker-compose down --remove-orphans

Write-Host ""
Write-Host "✅ KR-AI-Engine Consolidated Stack stopped!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Show container status
Write-Host "📊 Container Status:" -ForegroundColor Cyan
$containers = docker ps --filter "name=krai-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
if ($containers) {
    Write-Host $containers -ForegroundColor White
} else {
    Write-Host "   No KRAI containers running" -ForegroundColor Yellow
}

Write-Host ""
if (-not $RemoveVolumes) {
    Write-Host "💾 Volumes preserved:" -ForegroundColor Cyan
    Write-Host "   ├─ krai_logs (API logs)" -ForegroundColor White
    Write-Host "   ├─ krai_uploads (Uploaded files)" -ForegroundColor White
    Write-Host "   ├─ supabase_db_data (Database)" -ForegroundColor White
    Write-Host "   ├─ supabase_storage_data (File storage)" -ForegroundColor White
    Write-Host "   ├─ ollama_data (AI models)" -ForegroundColor White
    Write-Host "   ├─ openwebui_data (Chat data)" -ForegroundColor White
    Write-Host "   └─ redis_data (Cache)" -ForegroundColor White
    Write-Host ""
    Write-Host "To remove volumes: .\stop_krai.ps1 -RemoveVolumes" -ForegroundColor Yellow
} else {
    Write-Host "All volumes removed!" -ForegroundColor Red
}

Write-Host "🔄 To restart: .\start_krai.ps1" -ForegroundColor Green
