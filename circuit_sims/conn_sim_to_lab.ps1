# 1. Launch the simulators
Start-Process "C:\Path\To\SimulIDE\simulide.exe"
Start-Process "C:\Path\To\PICSimLab\picsimlab.exe"

# 2. Automate the serial bridge connection
# Use mpremote to connect to the internal Windows virtual serial link
Start-Process "mpremote" -ArgumentList "connect COM5 repl"

# 3. Trigger the file-watcher for live-reload (if using the 'entr' equivalent)
# This will watch your script and flash it instantly upon save
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = ".\src"
$watcher.Filter = "*.py"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

Register-ObjectEvent $watcher "Changed" -Action {
    mpremote connect COM5 cp $Event.SourceEventArgs.FullPath :main.py
    Write-Host "Auto-flashed new code to virtual board."
}