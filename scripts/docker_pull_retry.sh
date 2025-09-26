#!/bin/bash

# Docker Pull Retry Script with Exponential Backoff
# Fixes AWS ECR Rate Limit issues

set -e

# Configuration
MAX_RETRIES=5
INITIAL_DELAY=10
BACKOFF_MULTIPLIER=2

# Function to pull image with retry logic
pull_image_with_retry() {
    local image=$1
    local attempt=1
    local delay=$INITIAL_DELAY
    
    while [ $attempt -le $MAX_RETRIES ]; do
        echo "🔄 Attempt $attempt/$MAX_RETRIES: Pulling $image"
        
        if docker pull "$image" 2>/dev/null; then
            echo "✅ Successfully pulled: $image"
            return 0
        else
            if [ $attempt -eq $MAX_RETRIES ]; then
                echo "❌ Failed to pull $image after $MAX_RETRIES attempts"
                return 1
            fi
            
            echo "⏳ Failed. Waiting ${delay}s before retry..."
            sleep $delay
            delay=$((delay * BACKOFF_MULTIPLIER))
            attempt=$((attempt + 1))
        fi
    done
}

# Function to pull all Supabase images
pull_supabase_images() {
    echo "🚀 Starting Supabase image pulls with retry logic..."
    
    local images=(
        "public.ecr.aws/supabase/postgres:17.6.1.002"
        "public.ecr.aws/supabase/storage-api:v1.11.0" 
        "public.ecr.aws/supabase/postgrest:v12.0.1"
        "public.ecr.aws/supabase/gotrue:v2.158.1"
        "public.ecr.aws/supabase/kong:2.8.1.0"
    )
    
    local failed_images=()
    
    for image in "${images[@]}"; do
        if ! pull_image_with_retry "$image"; then
            failed_images+=("$image")
        fi
        echo "---"
    done
    
    if [ ${#failed_images[@]} -eq 0 ]; then
        echo "🎉 All Supabase images pulled successfully!"
        return 0
    else
        echo "❌ Failed to pull the following images:"
        for image in "${failed_images[@]}"; do
            echo "  - $image"
        done
        echo ""
        echo "💡 Suggestions:"
        echo "   1. Check internet connection"
        echo "   2. Try again later (rate limits reset)"
        echo "   3. Use alternative setup: ./start_krai_alternative.sh"
        return 1
    fi
}

# Main execution
if [ "$1" = "--single" ] && [ -n "$2" ]; then
    # Pull single image
    pull_image_with_retry "$2"
else
    # Pull all Supabase images
    pull_supabase_images
fi
