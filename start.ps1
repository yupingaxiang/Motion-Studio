# Motion Studio Windows startup script
# One-click: init + backend(8000) + frontend(5173)
# Usage: .\start.ps1   or   .\start.ps1 -SkipInit -BackendOnly

param(
    [switch]$SkipInit,
    [switch]$SkipRender,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

# ---- Paths ----
$vp = Join-Path $root ".venv\Scripts\python.exe"
$dshNodeDir = "C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin"
$node = Join-Path $dshNodeDir "node.exe"
$pnpm = "C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\pnpm\bin\pnpm.mjs"

# ---- Put DSH Node FIRST in PATH so pnpm/vite use Node v24, not the old system Node v12 ----
if (Test-Path $node) {
    $env:PATH = "$dshNodeDir;" + $env:PATH
} else {
    Write-Host "[WARN] DSH Node not found at $node, falling back to PATH node (may be too old)" -ForegroundColor Yellow
    $node = "node"
    $pnpm = "pnpm"
}

# ---- Check Python venv ----
if (-not (Test-Path $vp)) {
    Write-Host "[ERROR] Python venv not found: $vp" -ForegroundColor Red
    Write-Host "  Create it first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  .venv\Scripts\pip install fastapi `"uvicorn[standard]`" pydantic python-multipart aiofiles" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== Motion Studio ===" -ForegroundColor Cyan
Write-Host "Python: $vp"
Write-Host "Node:   $((& $node --version 2>&1))"
Write-Host "pnpm:   $((& $node $pnpm --version 2>&1))"
Write-Host "FFmpeg: $((& ffmpeg -version 2>&1 | Select-Object -First 1))"

# ---- Init ----
if (-not $SkipInit) {
    Write-Host "`n--- Init catalog & demo project ---" -ForegroundColor Cyan
    & $vp "scripts\motion_studio.py" init
}

# ---- Render template previews if missing ----
if (-not $SkipRender) {
    $needRender = $false
    $ids = @("TEXT-001","FLOW-001","COMP-001","DEMO-001","DATA-001","TRANS-001")
    foreach ($id in $ids) {
        $mp4 = Join-Path $root "library\motions\$id\preview.mp4"
        if (-not (Test-Path $mp4)) { $needRender = $true; break }
    }
    if ($needRender) {
        Write-Host "`n--- Rendering template previews (first run ~2 min) ---" -ForegroundColor Cyan
        & $vp "scripts\motion_studio.py" render-template-previews
    } else {
        Write-Host "`n--- Template previews ready ---" -ForegroundColor Green
    }
}

# ---- Start backend ----
function Start-Backend {
    Write-Host "`n--- Backend (http://127.0.0.1:8000) ---" -ForegroundColor Cyan
    $env:PYTHONIOENCODING = "utf-8"
    & $vp -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
}

# ---- Start frontend ----
function Start-Frontend {
    Write-Host "`n--- Frontend (http://localhost:5173) ---" -ForegroundColor Cyan
    Push-Location (Join-Path $root "frontend")
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing frontend deps..."
        & $node $pnpm install --no-frozen-lockfile
    }
    # Run vite dev server with DSH node (already first in PATH)
    & $node "node_modules\vite\bin\vite.js" --host
    Pop-Location
}

# ---- Main ----
if ($BackendOnly) {
    Start-Backend
} elseif ($FrontendOnly) {
    Start-Frontend
} else {
    Write-Host "`n--- Starting backend + frontend ---" -ForegroundColor Cyan
    Write-Host "Backend: http://127.0.0.1:8000/api  (docs: /docs)" -ForegroundColor Gray
    Write-Host "Frontend: http://localhost:5173" -ForegroundColor Gray
    Write-Host "`nPress Ctrl+C to stop." -ForegroundColor Yellow

    # Backend in background job
    $env:PYTHONIOENCODING = "utf-8"
    $backendJob = Start-Job -ScriptBlock {
        param($vp, $root)
        Set-Location $root
        $env:PYTHONIOENCODING = "utf-8"
        & $vp -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
    } -ArgumentList $vp, $root

    # Give backend 3s head start
    Start-Sleep -Seconds 3

    # Frontend in foreground
    Push-Location (Join-Path $root "frontend")
    if (-not (Test-Path "node_modules")) {
        & $node $pnpm install --no-frozen-lockfile
    }
    try {
        & $node "node_modules\vite\bin\vite.js" --host
    } finally {
        Pop-Location
        Write-Host "`nStopping backend..."
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -ErrorAction SilentlyContinue
    }
}
