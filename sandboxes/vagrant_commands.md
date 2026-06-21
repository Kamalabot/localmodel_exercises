# 1. Boot ONLY the Alpine Frontend Node
vagrant plugin install vagrant-vbguest vagrant-disksize vagrant-share
vagrant up frontend-alpine

# 2. Boot ONLY the Debian Database Node
vagrant up db-debian

# 3. Boot ONLY the Ubuntu Backend Node
vagrant up backend-ubuntu

# Log into just the Debian machine to look at its SQLite database
vagrant ssh db-debian

# Shut down only the Ubuntu worker node to test how your frontend handles service dropouts
vagrant halt backend-ubuntu

# Force a configuration rebuild/provision on just the Alpine machine
vagrant reload frontend-alpine --provision

    reload: Restarts the virtual machine safely so it picks up any configuration changes in your Vagrantfile.

    --provision: Forces Vagrant to re-run your shell installation scripts, allowing it to execute your newly updated script name instead of skipping it.

Update your frontend-alpine block to explicitly tell Vagrant to use rsync for file mapping. This guarantees your scripts appear inside /vagrant/ regardless of your VirtualBox version.

choco install rsync

### When the VBOxes become stale

vboxmanage unregistervm {e067a537-698a-4f93-bc2c-23483fb60076}
vboxmanage unregistervm {5d0a8378-83d8-48af-b9e9-36444a57a9e6}
vboxmanage unregistervm {73952d0a-4de2-498d-b073-f27c9b93c2d4}

taskkill /F /IM VBoxSVC.exe /T
taskkill /F /IM VirtualBox.exe /T
taskkill /F /IM vagrant.exe /T