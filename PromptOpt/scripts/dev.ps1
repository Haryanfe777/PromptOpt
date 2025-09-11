param(
  [string]$OpenAIKey = $env:OPENAI_API_KEY
)

Write-Host "== Backend setup =="
Set-Location ../backend
if (-not (Test-Path .venv)) { py -m venv .venv }
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path app.db)) { alembic upgrade head; python -m app.utils.seed }

Write-Host "Starting backend on http://127.0.0.1:8000 ..."
Start-Process powershell -ArgumentList "-NoProfile","-Command","$env:OPENAI_API_KEY='$OpenAIKey'; cd $(Get-Location).Path; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" | Out-Null

Write-Host "== Frontend setup =="
Set-Location ../frontend
npm install
Write-Host "Starting frontend on http://localhost:8080 ..."
Start-Process powershell -ArgumentList "-NoProfile","-Command","cd $(Get-Location).Path; npm start" | Out-Null

Write-Host "Launched backend and frontend in separate windows."
