# Quick Test Script for MaleCare Chatbot API
# Run this after starting the server with: uvicorn app.main:app --reload

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Testing MaleCare Chatbot API" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "Test 1: Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✓ Health check passed:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Submit Intake Form
Write-Host "`nTest 2: Submit Intake Form..." -ForegroundColor Yellow
$intakeData = @{
    user_id = "test_user_123"
    cancer_type = "breast cancer"
    stage = "stage 2"
    age = 45
    sex = "female"
    location = "California"
    comorbidities = @("diabetes")
    prior_treatments = @("chemotherapy")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/intake" -Method Post -Body $intakeData -ContentType "application/json"
    Write-Host "✓ Intake submitted:" -ForegroundColor Green
    Write-Host "   Bot: $($response.response)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Intake failed: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Send a Message
Write-Host "`nTest 3: Send a Chat Message..." -ForegroundColor Yellow
$messageData = @{
    user_id = "test_user_123"
    message = "Find me clinical trials in Los Angeles"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/message" -Method Post -Body $messageData -ContentType "application/json"
    Write-Host "✓ Message sent:" -ForegroundColor Green
    Write-Host "   Bot: $($response.response)" -ForegroundColor Cyan
    if ($response.trials) {
        Write-Host "`n   Found $($response.trials.Count) trial(s):" -ForegroundColor Green
        foreach ($trial in $response.trials) {
            Write-Host "     - $($trial.title)" -ForegroundColor White
            Write-Host "       Phase: $($trial.phase) | Status: $($trial.status)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "✗ Message failed: $_" -ForegroundColor Red
    exit 1
}

# Test 4: Say Goodbye
Write-Host "`nTest 4: Say Goodbye..." -ForegroundColor Yellow
$goodbyeData = @{
    user_id = "test_user_123"
    message = "Thanks, goodbye!"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/message" -Method Post -Body $goodbyeData -ContentType "application/json"
    Write-Host "✓ Goodbye sent:" -ForegroundColor Green
    Write-Host "   Bot: $($response.response)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Goodbye failed: $_" -ForegroundColor Red
    exit 1
}

# Test 5: End Session
Write-Host "`nTest 5: End Session..." -ForegroundColor Yellow
$endData = @{
    user_id = "test_user_123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/end-session" -Method Post -Body $endData -ContentType "application/json"
    Write-Host "✓ Session ended: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ End session failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " All Tests Passed! ✓" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
