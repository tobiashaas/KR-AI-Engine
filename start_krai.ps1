# 🚀 KR-AI-Engine - Consolidated Stack Startup (PowerShell)
# Single Source of Truth für alle Services
# Verwendet die konsolidierte Docker-Compose-Datei

param(
    [switch]$Verbose
)

Write-Host "🚀 Starting KR-AI-Engine Consolidated Stack..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "   Please copy .env.template to .env and configure your settings." -ForegroundColor Yellow
    exit 1
}

# Load environment variables from .env
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

$KRAI_API_PORT = if ($env:KRAI_API_PORT) { $env:KRAI_API_PORT } else { "8001" }

Write-Host "🔧 Environment Configuration:" -ForegroundColor Cyan
Write-Host "   ├─ API Port: $KRAI_API_PORT" -ForegroundColor White
Write-Host "   ├─ Supabase: Port 54321 (API) and 54323 (Studio)" -ForegroundColor White
Write-Host "   ├─ Ollama: Port 11434" -ForegroundColor White
Write-Host "   ├─ OpenWebUI: Port 8080" -ForegroundColor White
Write-Host "   ├─ Redis: Port 6379" -ForegroundColor White
Write-Host "   └─ PostgreSQL: Port 54322" -ForegroundColor White

Write-Host ""
Write-Host "🐳 Starting Consolidated Docker Stack..." -ForegroundColor Blue

# Stop any existing stacks first
Write-Host "🧹 Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans 2>$null

# Start the optimized stack
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Health checks
Write-Host ""
Write-Host "🔍 Checking service health..." -ForegroundColor Cyan

# Check Ollama
Write-Host "   ├─ Ollama: " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Running" -ForegroundColor Green
    } else {
        Write-Host "❌ Not ready" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Not ready" -ForegroundColor Red
}

# Check Supabase
Write-Host "   ├─ Supabase API: " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:54321/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Running" -ForegroundColor Green
    } else {
        Write-Host "❌ Not ready" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Not ready" -ForegroundColor Red
}

# Check KRAI API
Write-Host "   ├─ KRAI API: " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$KRAI_API_PORT/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Running" -ForegroundColor Green
    } else {
        Write-Host "❌ Not ready (may take a few more seconds)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Not ready (may take a few more seconds)" -ForegroundColor Yellow
}

# Check OpenWebUI  
Write-Host "   ├─ OpenWebUI: " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Running" -ForegroundColor Green
    } else {
        Write-Host "❌ Not ready" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Not ready" -ForegroundColor Red
}

# Check Redis
Write-Host "   └─ Redis: " -NoNewline
try {
    $result = docker exec krai-redis redis-cli ping 2>$null
    if ($result -eq "PONG") {
        Write-Host "✅ Running" -ForegroundColor Green
    } else {
        Write-Host "❌ Not ready" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Not ready" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 KR-AI-Engine Consolidated Stack Started!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📡 Service URLs:" -ForegroundColor Cyan
Write-Host "   ├─ 🚀 KRAI API:        http://localhost:$KRAI_API_PORT" -ForegroundColor White
Write-Host "   ├─ 💬 Chat Interface:  http://localhost:8080" -ForegroundColor White
Write-Host "   ├─ 🗄️  Supabase API:   http://localhost:54321" -ForegroundColor White
Write-Host "   ├─ 🎛️  Supabase Studio: http://localhost:54323" -ForegroundColor White
Write-Host "   ├─ 🤖 Ollama API:      http://localhost:11434" -ForegroundColor White
Write-Host "   └─ 🔴 Redis:           localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "📊 Health Checks:" -ForegroundColor Cyan
Write-Host "   ├─ 🚀 KRAI Health:     curl http://localhost:$KRAI_API_PORT/health" -ForegroundColor White
Write-Host "   ├─ 🤖 Ollama Models:   curl http://localhost:11434/api/tags" -ForegroundColor White
Write-Host "   └─ 🗄️  Supabase:       curl http://localhost:54321/health" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop the stack: docker-compose down" -ForegroundColor Yellow
Write-Host "📜 To view logs:      docker-compose logs -f [service-name]" -ForegroundColor Yellow
Write-Host ""

# Pull Ollama models if they don't exist
Write-Host "🤖 Checking AI Models..." -ForegroundColor Blue
Start-Sleep -Seconds 5

# Check if models exist and pull if needed
$models = @("llama3.2:3b", "llava:7b", "embeddinggemma")
foreach ($model in $models) {
    $modelExists = docker exec krai-ollama ollama list 2>$null | Select-String $model
    if (-not $modelExists) {
        Write-Host "⬇️ Pulling $model..." -ForegroundColor Yellow
        Start-Job -ScriptBlock { docker exec krai-ollama ollama pull $using:model } | Out-Null
    }
}

# Wait for all background jobs to complete
Get-Job | Wait-Job | Out-Null
Get-Job | Remove-Job

Write-Host "✅ KR-AI-Engine Consolidated Stack is fully operational!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Access KRAI API: http://localhost:$KRAI_API_PORT" -ForegroundColor White
Write-Host "   2. Open Chat Interface: http://localhost:8080" -ForegroundColor White
Write-Host "   3. Check Supabase Studio: http://localhost:54323" -ForegroundColor White
Write-Host "   4. Upload documents via API or Chat Interface" -ForegroundColor White
