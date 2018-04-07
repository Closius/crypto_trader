#!/bin/bash
#
# Ubuntu 16.04
#
#
#
#
#
#
POSTGRES_PASSWORD='postgresPassworD'
TRADER_PASSWORD='traderPassworD'
#
#
apt-get -y install python3 python3-pip python3-dev libpq-dev postgresql postgresql-contrib
pip3 install --upgrade pip
echo "========================================================="
echo ""
echo "                  Install PostgreSql"
echo ""
echo "========================================================="
cmd_to_pass="ALTER ROLE postgres WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';"
su postgres -c "psql -c \"$cmd_to_pass\""
cmd_to_pass="CREATE USER trader WITH ENCRYPTED PASSWORD '$TRADER_PASSWORD';"
su postgres -c "psql -c \"$cmd_to_pass\""
su postgres -c "psql -c \"CREATE DATABASE crypto_trader_db;\""
su postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE crypto_trader_db TO trader;\""
# These are all recommendations from the Django project itself:
cmd_to_pass="ALTER ROLE trader SET client_encoding TO 'utf8';"
su postgres -c "psql -c \"$cmd_to_pass\""
cmd_to_pass="ALTER ROLE trader SET default_transaction_isolation TO 'read committed';"
su postgres -c "psql -c \"$cmd_to_pass\""
cmd_to_pass="ALTER ROLE trader SET timezone TO 'UTC';"
su postgres -c "psql -c \"$cmd_to_pass\""
#
# install postgresql (Postgres by default listen localhost only:)
#
# Get access from anywhere. Because we dont have a http server and app server, 
# so this it not good solution because of safety. 
#
# postgresql.conf       (located in /etc/...)
# listen_addresses = '*'
# pg_hba.conf           (It allows access to all databases for all users with an encrypted password)
# # TYPE DATABASE USER CIDR-ADDRESS  METHOD
# host  all  all 0.0.0.0/0 md5
# sudo service postgresql restart
#
# Get remote access to postgresql:
#
# psql --host='66.666.666.666' --port=5432 --username='trader' --dbname='trader_db'
#
# export PGPASSWORD='kokokokoko'; psql --host='66.666.666.666' --port=5432 --username='trader' --dbname='trader_db'
#
#
echo "========================================================="
echo ""
echo "                  Install TA-lib"
echo ""
echo "========================================================="
#
apt-get -y install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xvf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
make install
cd ..
rm ta-lib-0.4.0-src.tar.gz
rm -rf ta-lib
echo "========================================================="
echo ""
echo "                  Git"
echo ""
echo "========================================================="
# >> cd ~/.ssh
# >> ssh-keygen
# >> echo 'Host bitbucket.org
# RSAAuthentication yes
# IdentityFile ~/.ssh/bitbucket_id_rsa' > config
# >> cat ~/.ssh/bitbucket_id_rsa.pub 
#
# Add bitbucket_id_rsa.pub to access keys on your repository bitbucket.org
echo "========================================================="
echo ""
echo "                  Django"
echo ""
echo "========================================================="
#
#
#
#
#
export USERNAME=crypto_trader
export MY_HOME=/home/$USERNAME
export PROJECT_DIR=$MY_HOME/crypto_trader
#
#
pip3 install virtualenv
cd $PROJECT_DIR
su crypto_trader -c "virtualenv virtualenv_crypto_trader --python=python3.5"
source virtualenv_crypto_trader/bin/activate
pip3 install django==2.0.3
pip3 install gunicorn==19.7.1
pip3 install requests
pip3 install psycopg2==2.7.4
pip3 install btfxwss #==1.1.16
pip3 install numpy #==1.14.1
pip3 install TA-Lib #==0.4.16
#
python manage.py makemigrations # activate if DATABASE is clear
python manage.py migrate # activate if DATABASE is clear
# python manage.py createsuperuser # activate if DATABASE is clear
#
python manage.py collectstatic
source deactivate
#
echo "========================================================="
echo ""
echo "                  Gunicorn"
echo ""
echo "========================================================="
cd /etc/systemd/system
touch gunicorn_crypto_trader.service
echo "[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=$USERNAME
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/virtualenv_crypto_trader/bin/gunicorn --access-logfile - --workers 3 --bind unix:$PROJECT_DIR/crypto_trader.sock server.wsgi:application

[Install]
WantedBy=multi-user.target
" | sudo tee -a gunicorn_crypto_trader.service
#
#
#
systemctl start gunicorn_crypto_trader
systemctl enable gunicorn_crypto_trader
# systemctl status gunicorn_crypto_trader
#
# sudo systemctl daemon-reload
# sudo systemctl restart gunicorn
#
echo "========================================================="
echo ""
echo "                  Nginx"
echo ""
echo "========================================================="
apt-get -y install nginx
cd /etc/nginx/sites-available
#
#touch crypto_trader
echo "server {
    listen 80;
    server_name \"\";

    access_log off;
    log_not_found off;

    location /static/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/crypto_trader.sock;
    }
}
" | sudo tee -a crypto_trader
ln -s /etc/nginx/sites-available/crypto_trader /etc/nginx/sites-enabled/crypto_trader
rm /etc/nginx/sites-enabled/default
systemctl restart nginx
