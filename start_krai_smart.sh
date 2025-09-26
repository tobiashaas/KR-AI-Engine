#!/bin/bash

# KR-AI-Engine Smart Startup Script
# Automatically handles AWS ECR Rate Limits with intelligent fallback

set -e

echo "🚀 KR-AI-Engine Smart Startup"
echo "   Handles AWS ECR Rate Limits automatically"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RETRY_ATTEMPTS=3
RETRY_DELAY=15

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker ist nicht verfügbar. Bitte Docker starten.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker ist verfügbar${NC}"
}

# Test ECR connectivity
test_ecr_connectivity() {
    echo -e "${BLUE}🔍 Teste AWS ECR Connectivity...${NC}"
    
    # Try to pull a small image as test
    if timeout 30 docker pull public.ecr.aws/supabase/postgres:17.6.1.002 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ AWS ECR ist erreichbar${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  AWS ECR Rate Limits oder Netzwerkprobleme erkannt${NC}"
        return 1
    fi
}

# Strategy 1: Try Supabase CLI (Recommended)
try_supabase_cli() {
    echo -e "${BLUE}🎯 Strategie 1: Supabase CLI${NC}"
    
    if ! command -v supabase &> /dev/null; then
        echo -e "${YELLOW}⚠️  Supabase CLI nicht installiert${NC}"
        return 1
    fi
    
    echo "   Starte Supabase mit CLI..."
    
    # Stop any running instance first
    supabase stop 2>/dev/null || true
    
    # Start with CLI
    if supabase start; then
        echo -e "${GREEN}✅ Supabase CLI erfolgreich gestartet!${NC}"
        echo ""
        echo -e "${GREEN}📋 Supabase Services verfügbar:${NC}"
        echo "   🌐 API: http://127.0.0.1:54321"
        echo "   🗄️  DB:  postgresql://postgres:postgres@127.0.0.1:54322/postgres"
        echo "   🎨 UI:  http://127.0.0.1:54323"
        return 0
    else
        echo -e "${RED}❌ Supabase CLI fehlgeschlagen${NC}"
        return 1
    fi
}

# Strategy 2: Docker Compose with retry
try_docker_compose_retry() {
    echo -e "${BLUE}🎯 Strategie 2: Docker Compose mit Retry${NC}"
    
    local attempt=1
    while [ $attempt -le $RETRY_ATTEMPTS ]; do
        echo "   Versuch $attempt/$RETRY_ATTEMPTS..."
        
        # Pre-pull images with retry script
        if [ -x "./scripts/docker_pull_retry.sh" ]; then
            echo "   📦 Ziehe Images mit Retry-Logic..."
            if ./scripts/docker_pull_retry.sh; then
                echo "   ✅ Alle Images erfolgreich geladen"
            else
                echo "   ⚠️  Einige Images fehlgeschlagen, versuche trotzdem..."
            fi
        fi
        
        # Try docker compose with optimized configuration
        if docker compose up -d; then
            echo -e "${GREEN}✅ Docker Compose erfolgreich gestartet!${NC}"
            
            # Wait for health checks
            echo "   ⏳ Warte auf Health Checks..."
            sleep 10
            
            # Verify services
            if docker compose ps | grep -q "healthy"; then
                echo -e "${GREEN}✅ Services sind gesund${NC}"
                return 0
            fi
        fi
        
        echo -e "${YELLOW}   ⚠️  Versuch $attempt fehlgeschlagen${NC}"
        
        if [ $attempt -lt $RETRY_ATTEMPTS ]; then
            echo "   ⏳ Warte ${RETRY_DELAY}s vor nächstem Versuch..."
            sleep $RETRY_DELAY
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ Docker Compose nach $RETRY_ATTEMPTS Versuchen fehlgeschlagen${NC}"
    return 1
}

# Strategy 3: Alternative Images  
try_alternative_images() {
    echo -e "${BLUE}🎯 Strategie 3: Alternative Images${NC}"
    
    if [ ! -f "docker-compose.alternative.yml" ]; then
        echo -e "${RED}❌ docker-compose.alternative.yml nicht gefunden${NC}"
        return 1
    fi
    
    echo "   Verwende Docker Hub Images statt AWS ECR..."
    
    if docker compose -f docker-compose.alternative.yml up -d; then
        echo -e "${GREEN}✅ Alternative Images erfolgreich gestartet!${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  HINWEIS: Vereinfachte Supabase-Alternative aktiv${NC}"
        echo "   🗄️  DB:      http://localhost:54322"
        echo "   ☁️  Storage: http://localhost:54321 (Minio)"
        echo "   📊 Admin:   http://localhost:54324"
        return 0
    else
        echo -e "${RED}❌ Alternative Images fehlgeschlagen${NC}"
        return 1
    fi
}

# Show final status
show_status() {
    echo ""
    echo -e "${GREEN}🎉 KR-AI-Engine erfolgreich gestartet!${NC}"
    echo ""
    echo -e "${BLUE}📋 Nächste Schritte:${NC}"
    echo "   1. Teste API: curl http://localhost:8001/health"
    echo "   2. Öffne Supabase Studio: http://127.0.0.1:54323"
    echo "   3. Verarbeite ein Dokument mit dem Processor"
    echo ""
    echo -e "${BLUE}📄 Logs anzeigen:${NC}"
    echo "   docker logs -f <container_name>"
    echo ""
}

# Main execution
main() {
    echo "🔍 Starte intelligente Fehlerbehandlung..."
    echo ""
    
    check_docker
    
    # Try strategies in order of preference
    if try_supabase_cli; then
        show_status
        exit 0
    fi
    
    echo ""
    echo -e "${YELLOW}🔄 Fallback zu Docker Compose...${NC}"
    
    if try_docker_compose_retry; then
        show_status
        exit 0
    fi
    
    echo ""
    echo -e "${YELLOW}🔄 Fallback zu Alternative Images...${NC}"
    
    if try_alternative_images; then
        show_status
        exit 0
    fi
    
    # All strategies failed
    echo ""
    echo -e "${RED}❌ ALLE STRATEGIEN FEHLGESCHLAGEN${NC}"
    echo ""
    echo -e "${BLUE}💡 Mögliche Lösungen:${NC}"
    echo "   1. Internet-Verbindung prüfen"
    echo "   2. Später nochmal versuchen (Rate Limits resetten)"
    echo "   3. VPN verwenden (andere IP-Adresse)"
    echo "   4. AWS CLI konfigurieren für authentifizierte Pulls"
    echo "   5. Manual: supabase start"
    echo ""
    exit 1
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "KR-AI-Engine Smart Startup Script"
        echo ""
        echo "VERWENDUNG:"
        echo "   $0                 # Automatischer Start mit Fallback"
        echo "   $0 --supabase-cli  # Nur Supabase CLI versuchen"
        echo "   $0 --docker-compose # Nur Docker Compose versuchen" 
        echo "   $0 --alternative   # Nur Alternative Images versuchen"
        echo ""
        exit 0
        ;;
    --supabase-cli)
        check_docker
        try_supabase_cli && show_status
        ;;
    --docker-compose)
        check_docker
        try_docker_compose_retry && show_status
        ;;
    --alternative)
        check_docker
        try_alternative_images && show_status
        ;;
    *)
        main
        ;;
esac
