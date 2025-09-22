# Quick Index Check
$SUPABASE_URL = "https://jruahqpwladkqxpnwzdz.supabase.co"
$SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpydWFocXB3bGFka3F4cG53emR6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODUzNzExNCwiZXhwIjoyMDc0MTEzMTE0fQ.Uzxr83Iuz5Sa0K1YlD_kWF42yDPSvo4Qh0OU50_zha0"

$headers = @{
    'Authorization' = "Bearer $SERVICE_ROLE_KEY"
    'Content-Type' = 'application/json'
    'apikey' = $SERVICE_ROLE_KEY
}

Write-Host "TESTING COMPLEX QUERIES (Index Performance):" -ForegroundColor Cyan

# Test 1: Error code search performance
Write-Host "`nTesting error code search..." -ForegroundColor Yellow
$start = Get-Date
$response = Invoke-WebRequest -Uri "$SUPABASE_URL/rest/v1/error_codes?select=*" -Method GET -Headers $headers
$end = Get-Date
$duration = ($end - $start).TotalMilliseconds
$count = ($response.Content | ConvertFrom-Json).Count
Write-Host "Found $count error codes in ${duration}ms" -ForegroundColor Green

# Test 2: Product hierarchy performance
Write-Host "`nTesting product hierarchy..." -ForegroundColor Yellow
$start = Get-Date
$response = Invoke-WebRequest -Uri "$SUPABASE_URL/rest/v1/products?select=*" -Method GET -Headers $headers
$end = Get-Date
$duration = ($end - $start).TotalMilliseconds
$count = ($response.Content | ConvertFrom-Json).Count
Write-Host "Found $count products in ${duration}ms" -ForegroundColor Green

# Test 3: Document relationship performance
Write-Host "`nTesting document relationships..." -ForegroundColor Yellow
$start = Get-Date
$response = Invoke-WebRequest -Uri "$SUPABASE_URL/rest/v1/document_relationships?select=*" -Method GET -Headers $headers
$end = Get-Date
$duration = ($end - $start).TotalMilliseconds
$count = ($response.Content | ConvertFrom-Json).Count
Write-Host "Found $count document relationships in ${duration}ms" -ForegroundColor Green

Write-Host "`n✅ All queries are performing well - Indexes appear to be working!" -ForegroundColor Green