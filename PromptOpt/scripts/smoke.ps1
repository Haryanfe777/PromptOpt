param(
  [string]$Base = "http://127.0.0.1:8000",
  [string]$User = "admin",
  [string]$Pass = "admin"
)

Write-Host "== Health =="
try { (Invoke-WebRequest -UseBasicParsing "$Base/health").Content } catch { Write-Error $_; exit 1 }

Write-Host "== Login =="
$login = Invoke-RestMethod -Uri "$Base/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body "username=$User&password=$Pass"
$token = $login.access_token
if (-not $token) { throw "No token" }

Write-Host "== Me =="
Invoke-RestMethod -Uri "$Base/me" -Headers @{ Authorization = "Bearer $token" }

Write-Host "== Prompts =="
Invoke-RestMethod -Uri "$Base/prompts"

Write-Host "== Chat =="
$body = @{ message = "What are our PTO policies?"; evaluate = $true } | ConvertTo-Json
Invoke-RestMethod -Uri "$Base/chat" -Method Post -ContentType "application/json" -Headers @{ Authorization = "Bearer $token" } -Body $body

Write-Host "Smoke tests completed."
