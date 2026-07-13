# 0. Openup the ports 
netsh advfirewall firewall add rule name="Allow Host-Only Ping" protocol=icmpv4:8,any dir=in action=allow profile=any
netsh advfirewall firewall add rule name="Allow SSH Outbound" protocol=TCP remoteport=22 dir=out action=allow profile=any
netsh advfirewall firewall add rule name="Allow SSH Inbound" protocol=TCP localport=22 dir=in action=allow profile=any

# 1. Execute the internal daemon installer script bundled with Choco
& "C:\Program Files\OpenSSH-Win64\install-sshd.ps1"

# 2. Configure the new services to boot automatically
Set-Service -Name sshd -StartupType Automatic
Set-Service -Name ssh-agent -StartupType Automatic
Start-Service sshd
Start-Service ssh-agent

# 3. Open the Inbound Windows Defender Firewall Rule for Port 22
New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -Profile Any

# 4. Set PowerShell 5.1 as the Default Remote Shell Environment
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force