#!/usr/bin/env bash

# Copy autostart file to relevant dir
# remove full file path to avoid V0 issues 6/6/22
sudo cp "/home/pi/v0/cd_alpha/setup/autostart" "/etc/xdg/lxsession/LXDE-pi/"








## Deamon to autostart all the time.


# Link the unit into the global systemd unit dir
# remove full file path to avoid V0 issues 6/6/22
sudo ln -fs "cd-alpha-starter.service" /lib/systemd/system/

# Enable it
sudo systemctl enable cd-alpha-starter.service
echo "Service installed, rebooting"
sudo shutdown -r now

# To stop service, run:
# service stop cd-alpha-starter
# To start again after stopping it:
# service start cd-alpha-starter