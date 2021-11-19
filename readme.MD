# monitor and resize Digital ocean volume

# Create .env file

create a file named `.env` 

Add the following:

> Generate in the API section of Digital Ocean
> Use whole numbers for the Percentages

TOKEN=<DIGITAL OCEAN API TOKEN>
VOLUME_NAME=volume-sfo3-02
INCREASE_BY_PERCENTAGE=1 
PERCENTAGE_TO_INCREASE=5

EMAIL_SMTP=smtp.123-reg.co.uk
EMAIL_PASS=<EMAIL PASSWORD>
EMAIL_FROM=john@maffaz.com
EMAIL_TO=mennovandevlees@gmail.com

Toggle the `SEND_EMAIL` flag in `includes/config.py` choose True / False to send emails.

# install
`sudo apt update && sudo apt upgrade -y`

`apt install python3-pip`

`pip3 install -r requirements.txt`

run
`python3 main.py`


# create systemd
``` bash 

cat<<-EOF > /etc/systemd/system/resize_hdd.service
[Unit]
Description=resize_hdd daemon
After=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
WorkingDirectory=/root/resize_hdd
ExecStart=python3 main.py
SyslogIdentifier=resize_hdd
StartLimitInterval=0
LimitNOFILE=65536
LimitNPROC=65536

[Install]
WantedBy=multi-user.target
EOF

```

`sudo systemctl daemon-reload`

`sudo chmod 755 /etc/systemd/system/resize_hdd.service`

`sudo systemctl enable resize_hdd.service`

`sudo service resize_hdd start `

`sudo service resize_hdd status`


# Check Logs
`tail -f /var/log/syslog`

`journalctl  -xefu resize_hdd`

