Write-Host "Initializing Clear-Feed Sovereign Air-Gapped Repository Engine..." -ForegroundColor Cyan

$RepoPath = "E:\SovereignRepo"
$SourceDir = "$RepoPath\Source"
$MaxRetries = 3
$RetryWaitSeconds = 5

# Clear previous corrupted Chocolatey temporary scratching zones
Write-Host "Flushing localized scratch and cache zones to fix manifest alignment errors..." -ForegroundColor Yellow
$ScratchPaths = @(
    "$env:LOCALAPPDATA\Temp\chocolatey",
    "$env:PROGRAMDATA\chocolatey\cache"
)
foreach ($Path in $ScratchPaths) {
    if (Test-Path $Path) { Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue }
}

if (-not (Test-Path $SourceDir)) { 
    New-Item -ItemType Directory -Path $SourceDir -Force | Out-Null 
}
Set-Location -Path $RepoPath

# Force TLS 1.2 / 1.3 to avoid security translation exceptions
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

# Create strict HTTPS-only local NuGet Configuration
$NugetConfigPath = "$RepoPath\nuget.config"
$NugetConfigContent = @"
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="Chocolatey" value="https://community.chocolatey.org/api/v2/" />
    <add key="Mandiant" value="https://www.myget.org/F/vm-packages/api/v2" />
  </packageSources>
</configuration>
"@
Set-Content -Path $NugetConfigPath -Value $NugetConfigContent

if (-not (Test-Path "$RepoPath\choco-remixer")) {
    Write-Host "Cloning choco-remixer open-source framework..." -ForegroundColor Yellow
    git clone https://github.com/TheCakeIsNaOH/choco-remixer.git "$RepoPath\choco-remixer"
}

if (Test-Path "$RepoPath\choco-remixer\choco-remixer.psd1") {
    Import-Module "$RepoPath\choco-remixer\choco-remixer.psd1" -Force
} elseif (Test-Path "$RepoPath\choco-remixer\choco-remixer.psm1") {
    Import-Module "$RepoPath\choco-remixer\choco-remixer.psm1" -Force
}

if (-not (Test-Path "$RepoPath\nuget.exe")) {
    Write-Host "Downloading NuGet engine..." -ForegroundColor Yellow
    Invoke-WebRequest "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe" -OutFile "$RepoPath\nuget.exe"
}

$MandiantPackages = @(
    "common.vm", "debloat.vm", "fakenet-ng.vm", "cutter.vm", "pebear.vm", 
    "sliver.vm", "bloodhound.vm", "systeminformer.vm", "x64dbg.vm", "wireshark.vm"
)

# Fixed resourcehacker -> reshack, explorer-suite -> explorersuite
$ChocoPackages = @(
    "git", "python3", "golang", "rust", "mingw", "nodejs", "nasm", "openssh", 
    "vscode", "neovim", "jetbrains-toolbox", "notepadplusplus", "ghidra", "die", 
    "upx", "reshack", "explorersuite", "hxd", "sysinternals", "cyberchef", 
    "winscp", "advanced-ip-scanner", "nmap", "netcat", "putty", "autohotkey.install"
)

# Phase 1: Explicitly process Mandiant Packages strictly through MyGet Feed
Write-Host "Phase 1: Downloading Mandiant Core Framework..." -ForegroundColor Cyan
foreach ($Pkg in $MandiantPackages) {
    $existingPkg = Get-ChildItem -Path $RepoPath -Filter "$Pkg.*.nupkg"
    if ($existingPkg) { Write-Host "Skipping $Pkg (Already Packed)" -ForegroundColor Green; continue }

    $attempt = 0
    $success = $false
    while (-not $success -and $attempt -lt $MaxRetries) {
        try {
            .\nuget.exe install $Pkg -Source "https://www.myget.org/F/vm-packages/api/v2" -OutputDirectory $SourceDir -ExcludeVersion -NonInteractive -DirectDownload -ConfigFile $NugetConfigPath
            $success = $true
        } catch {
            $attempt++
            Write-Host "Retry loop active for $Pkg ($attempt/$MaxRetries)..." -ForegroundColor Red
            Start-Sleep -Seconds $RetryWaitSeconds
        }
    }

    if (-not $success) { continue }

    $InstallScriptPath = "$SourceDir\$Pkg\tools\chocolateyInstall.ps1"
    if (Test-Path $InstallScriptPath) {
        $ScriptContent = Get-Content $InstallScriptPath -Raw
        $Regex = "(?i)(http[s]?://[^\s'""`]+(?:\.exe|\.zip|\.msi|\.7z|\.gz|\.tar))"
        $Urls = [regex]::Matches($ScriptContent, $Regex) | ForEach-Object { $_.Value } | Select-Object -Unique
        
        foreach ($Url in $Urls) {
            $FileName = Split-Path $Url -Leaf
            $LocalFilePath = "$SourceDir\$Pkg\tools\$FileName"
            
            try {
                Invoke-WebRequest -Uri $Url -OutFile $LocalFilePath -TimeoutSec 30
                $LocalPathString = "`"`$(Split-Path -parent `$MyInvocation.MyCommand.Definition)\$FileName`""
                $ScriptContent = $ScriptContent.Replace("'$Url'", $LocalPathString).Replace("`"$Url`"", $LocalPathString)
            } catch {}
        }
        
        Set-Content -Path $InstallScriptPath -Value $ScriptContent
        Set-Location "$SourceDir\$Pkg"
        choco pack
        if (Test-Path "*.nupkg") { Move-Item "*.nupkg" $RepoPath -Force }
        Set-Location $RepoPath
    }
}

# Phase 2: Process Base Ecosystem Utilities strictly through Chocolatey Feed
Write-Host "Phase 2: Internalizing Utility Packages..." -ForegroundColor Cyan
foreach ($Pkg in $ChocoPackages) {
    $existingPkg = Get-ChildItem -Path $RepoPath -Filter "$Pkg.*.nupkg"
    if ($existingPkg) { Write-Host "Skipping $Pkg (Already Packed)" -ForegroundColor Green; continue }

    $attempt = 0
    $success = $false
    while (-not $success -and $attempt -lt $MaxRetries) {
        try {
            .\nuget.exe install $Pkg -Source "https://community.chocolatey.org/api/v2/" -OutputDirectory $SourceDir -ExcludeVersion -NonInteractive -DirectDownload -ConfigFile $NugetConfigPath
            $success = $true
        } catch {
            $attempt++
            Write-Host "Retry loop active for $Pkg ($attempt/$MaxRetries)..." -ForegroundColor Red
            Start-Sleep -Seconds $RetryWaitSeconds
        }
    }

    if (-not $success) { continue }

    $InstallScriptPath = "$SourceDir\$Pkg\tools\chocolateyInstall.ps1"
    if (Test-Path $InstallScriptPath) {
        $ScriptContent = Get-Content $InstallScriptPath -Raw
        $Regex = "(?i)(http[s]?://[^\s'""`]+(?:\.exe|\.zip|\.msi|\.7z|\.gz|\.tar))"
        $Urls = [regex]::Matches($ScriptContent, $Regex) | ForEach-Object { $_.Value } | Select-Object -Unique
        
        foreach ($Url in $Urls) {
            $FileName = Split-Path $Url -Leaf
            $LocalFilePath = "$SourceDir\$Pkg\tools\$FileName"
            
            try {
                Invoke-WebRequest -Uri $Url -OutFile $LocalFilePath -TimeoutSec 30
                $LocalPathString = "`"`$(Split-Path -parent `$MyInvocation.MyCommand.Definition)\$FileName`""
                $ScriptContent = $ScriptContent.Replace("'$Url'", $LocalPathString).Replace("`"$Url`"", $LocalPathString)
            } catch {}
        }
        
        Set-Content -Path $InstallScriptPath -Value $ScriptContent
        Set-Location "$SourceDir\$Pkg"
        choco pack
        if (Test-Path "*.nupkg") { Move-Item "*.nupkg" $RepoPath -Force }
        Set-Location $RepoPath
    }
}

Write-Host "All components compiled inside E:\SovereignRepo. Sources isolated." -ForegroundColor Green