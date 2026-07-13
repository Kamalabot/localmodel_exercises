# 1. Target the system-wide OpenSSH configuration file path
$SshdConfigPath = "$env:ProgramData\ssh\sshd_config"

# 2. Extract contents and dynamically fix the Subsystem pointer to use the built-in binary matching the arch
if (Test-Path $SshdConfigPath) {
    (Get-Content $SshdConfigPath) -replace '^Subsystem\s+sftp.*', 'Subsystem sftp sftp-server.exe' | Set-Content $SshdConfigPath
}

# 3. Explicitly ensure the DefaultShell entry in the Registry doesn't swallow subsystem tasks
Set-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name "DefaultShellCommandOption" -Value "/c" -Force

# 4. Cycle the daemon to commit the state parameters
Restart-Service sshd