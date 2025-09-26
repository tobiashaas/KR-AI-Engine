#!/bin/bash

# Supabase Image Caching Script
# Pre-downloads and caches all Supabase images to avoid rate limits

set -e

CACHE_DIR="$HOME/.docker/supabase-cache"
CACHE_FILE="$CACHE_DIR/cached_images.txt"

# Create cache directory
mkdir -p "$CACHE_DIR"

# List of Supabase images with fallback alternatives
declare -A IMAGES=(
    ["postgres"]="public.ecr.aws/supabase/postgres:17.6.1.002|pgvector/pgvector:pg15"
    ["storage"]="public.ecr.aws/supabase/storage-api:v1.11.0|minio/minio:latest"
    ["postgrest"]="public.ecr.aws/supabase/postgrest:v12.0.1|postgrest/postgrest:v12.0.1"
    ["gotrue"]="public.ecr.aws/supabase/gotrue:v2.158.1|supabase/gotrue:v2.158.1"
    ["kong"]="public.ecr.aws/supabase/kong:2.8.1.0|kong:2.8"
)

# Function to check if image is cached
is_image_cached() {
    local image=$1
    docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$image$"
}

# Function to cache image with fallback
cache_image_with_fallback() {
    local service=$1
    local images_str=${IMAGES[$service]}
    
    IFS='|' read -ra IMAGE_LIST <<< "$images_str"
    
    echo "🔄 Caching images for service: $service"
    
    for image in "${IMAGE_LIST[@]}"; do
        echo "   Trying: $image"
        
        if is_image_cached "$image"; then
            echo "   ✅ Already cached: $image"
            echo "$image" >> "$CACHE_FILE.tmp"
            return 0
        fi
        
        if timeout 120 docker pull "$image" 2>/dev/null; then
            echo "   ✅ Successfully cached: $image"
            echo "$image" >> "$CACHE_FILE.tmp"
            return 0
        else
            echo "   ❌ Failed to pull: $image"
        fi
    done
    
    echo "   ❌ All alternatives failed for: $service"
    return 1
}

# Function to save cache manifest
save_cache_manifest() {
    if [ -f "$CACHE_FILE.tmp" ]; then
        mv "$CACHE_FILE.tmp" "$CACHE_FILE"
        echo "💾 Cache manifest saved to: $CACHE_FILE"
    fi
}

# Function to load from cache
load_cached_images() {
    echo "🔍 Checking cached images..."
    
    if [ ! -f "$CACHE_FILE" ]; then
        echo "❌ No cache manifest found"
        return 1
    fi
    
    local all_cached=true
    
    while IFS= read -r image; do
        if is_image_cached "$image"; then
            echo "✅ Cached: $image"
        else
            echo "❌ Missing: $image"
            all_cached=false
        fi
    done < "$CACHE_FILE"
    
    if [ "$all_cached" = true ]; then
        echo "🎉 All images are cached and ready!"
        return 0
    else
        echo "⚠️  Some images are missing from cache"
        return 1
    fi
}

# Function to clean cache
clean_cache() {
    echo "🧹 Cleaning Supabase image cache..."
    
    if [ -f "$CACHE_FILE" ]; then
        while IFS= read -r image; do
            echo "   Removing: $image"
            docker rmi "$image" 2>/dev/null || true
        done < "$CACHE_FILE"
        rm "$CACHE_FILE"
    fi
    
    docker system prune -f
    echo "✅ Cache cleaned"
}

# Main execution
main() {
    case "${1:-}" in
        --check)
            load_cached_images
            ;;
        --clean)
            clean_cache
            ;;
        --force)
            echo "🚀 Force caching all Supabase images..."
            rm -f "$CACHE_FILE.tmp"
            for service in "${!IMAGES[@]}"; do
                cache_image_with_fallback "$service" || true
            done
            save_cache_manifest
            ;;
        *)
            echo "🚀 Caching Supabase images..."
            
            # Check if already cached
            if load_cached_images; then
                exit 0
            fi
            
            # Cache missing images
            rm -f "$CACHE_FILE.tmp"
            for service in "${!IMAGES[@]}"; do
                cache_image_with_fallback "$service" || true
            done
            save_cache_manifest
            ;;
    esac
}

# Help
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    echo "Supabase Image Caching Script"
    echo ""
    echo "VERWENDUNG:"
    echo "   $0           # Cache missing images"
    echo "   $0 --check   # Check cache status"  
    echo "   $0 --clean   # Clean cache"
    echo "   $0 --force   # Force re-cache all images"
    echo ""
    echo "CACHE LOCATION: $CACHE_DIR"
    exit 0
fi

main "$@"
