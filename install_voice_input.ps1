# Voice Input Installation Script for AVA
# Run this script in PowerShell to install voice input dependencies

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "AVA Voice Input Installation Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Install Python packages
Write-Host ""
Write-Host "📦 Installing Python packages..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray

$packages = @(
    "openai-whisper",
    "audio-recorder-streamlit"
)

foreach ($package in $packages) {
    Write-Host "   Installing $package..." -ForegroundColor Gray
    pip install $package
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $package installed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to install $package" -ForegroundColor Red
    }
}

# Check for FFmpeg
Write-Host ""
Write-Host "🔍 Checking FFmpeg installation..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✅ FFmpeg found: $ffmpegVersion" -ForegroundColor Green
    $ffmpegInstalled = $true
} catch {
    Write-Host "❌ FFmpeg not found" -ForegroundColor Red
    $ffmpegInstalled = $false
}

if (-not $ffmpegInstalled) {
    Write-Host ""
    Write-Host "⚠️  FFmpeg is required but not installed" -ForegroundColor Yellow
    Write-Host "   FFmpeg is needed for audio processing" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To install FFmpeg:" -ForegroundColor Cyan
    Write-Host "1. Download from: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor White
    Write-Host "2. Download 'ffmpeg-release-essentials.zip'" -ForegroundColor White
    Write-Host "3. Extract to C:\ffmpeg" -ForegroundColor White
    Write-Host "4. Add to PATH:" -ForegroundColor White
    Write-Host '   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "Machine")' -ForegroundColor Gray
    Write-Host "5. Restart PowerShell" -ForegroundColor White
    Write-Host ""
    
    $response = Read-Host "Would you like to open the FFmpeg download page? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process "https://www.gyan.dev/ffmpeg/builds/"
    }
}

# Run test script
Write-Host ""
Write-Host "🧪 Running test script..." -ForegroundColor Yellow
python test_voice_input.py

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. If FFmpeg is not installed, follow the instructions above" -ForegroundColor White
Write-Host "2. Run: streamlit run app_streamlit.py" -ForegroundColor White
Write-Host "3. Navigate to Diagnosis page" -ForegroundColor White
Write-Host "4. Try the voice input feature!" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see VOICE_INPUT_SETUP.md" -ForegroundColor Gray
Write-Host ""
