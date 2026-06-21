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