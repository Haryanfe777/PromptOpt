param(
  [string]$OpenAIKey = $env:OPENAI_API_KEY
)

# Resolve project paths
$Root = (Resolve-Path "$PSScriptRoot\..\").Path
$BackendDir = Join-Path $Root 'backend'
$FrontendDir = Join-Path $Root 'frontend'

Write-Host "== Backend setup =="
Set-Location $BackendDir
if (-not (Test-Path .venv)) { py -m venv .venv }
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt | Out-Null
if (-not (Test-Path (Join-Path $BackendDir 'app.db'))) {
  alembic upgrade head
  python -m app.utils.seed
}

# Launch backend in a NEW window with the API key applied in that process
$backendCmd = "`$env:OPENAI_API_KEY='$OpenAIKey'; cd '$BackendDir'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process -FilePath "powershell.exe" -WorkingDirectory $BackendDir -ArgumentList "-NoExit","-NoProfile","-Command",$backendCmd -WindowStyle Normal | Out-Null

Write-Host "Starting backend on http://127.0.0.1:8000 ..."

Write-Host "== Frontend setup =="
Set-Location $FrontendDir
npm install | Out-Null

# Launch frontend in a NEW window
$frontendCmd = "cd '$FrontendDir'; npm start"
Start-Process -FilePath "powershell.exe" -WorkingDirectory $FrontendDir -ArgumentList "-NoExit","-NoProfile","-Command",$frontendCmd -WindowStyle Normal | Out-Null

Write-Host "Starting frontend on http://localhost:8080 ..."
Write-Host "Launched backend and frontend in separate windows."
