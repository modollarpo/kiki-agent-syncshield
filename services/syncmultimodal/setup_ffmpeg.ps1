# setup_ffmpeg.ps1
# Downloads ffmpeg for Windows, extracts it, and updates the PATH for the current session

$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$ffmpegZip = "ffmpeg-release-essentials.zip"
$ffmpegDir = "C:\xampp\htdocs\kiki_agent\ffmpeg"

# Download ffmpeg zip
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip

# Create target directory
if (!(Test-Path $ffmpegDir)) {
    New-Item -ItemType Directory -Path $ffmpegDir | Out-Null
}

# Extract ffmpeg
Expand-Archive -Path $ffmpegZip -DestinationPath $ffmpegDir -Force

# Find bin directory
$binPath = Get-ChildItem -Path $ffmpegDir -Recurse -Directory | Where-Object { $_.Name -eq "bin" } | Select-Object -First 1
if ($binPath) {
    $env:PATH = "$($binPath.FullName);$env:PATH"
    Write-Host "ffmpeg bin added to PATH: $($binPath.FullName)"
} else {
    Write-Host "ffmpeg bin directory not found."
}

# Cleanup
Remove-Item $ffmpegZip
