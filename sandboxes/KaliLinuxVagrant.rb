Vagrant.configure("2") do |config|
  config.vm.box = "kalilinux/rolling"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y git apache2 mariadb-server php php-mysqli php-gd libapache2-mod-php
    systemctl start mariadb
    mysql -e "CREATE USER 'user'@'127.0.0.1' IDENTIFIED BY 'pass';"
    mysql -e "GRANT ALL PRIVILEGES ON dvwa.* TO 'user'@'127.0.0.1';"
    mysql -e "FLUSH PRIVILEGES;"
    cd /var/www/html
    git clone https://github.com/digininja/DVWA.git dvwa
    chmod -R 777 dvwa
    cd dvwa/config
    cp config.inc.php.dist config.inc.php
    sed -i "s/'db_user'.*/'db_user' ] = 'user';/" config.inc.php
    sed -i "s/'db_password'.*/'db_password' ] = 'pass';/" config.inc.php
    sed -i 's/allow_url_fopen = Off/allow_url_fopen = On/' /etc/php/*/apache2/php.ini
    sed -i 's/allow_url_include = Off/allow_url_include = On/' /etc/php/*/apache2/php.ini
    systemctl restart apache2
  SHELL
end