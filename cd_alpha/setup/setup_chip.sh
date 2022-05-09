sudo apt update
sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev    pkg-config libgl1-mesa-dev libgles2-mesa-dev    python3-setuptools libgstreamer1.0-dev git-core    gstreamer1.0-plugins-{bad,base,good,ugly}    gstreamer1.0-{omx,alsa} python3-dev libmtdev-dev    xclip xsel libjpeg-dev
python3 -m pip install --upgrade --user pip setuptools
python3 -m pip install --upgrade --user Cython==0.29.10 pillow
python3 -m pip install --user kivy
pip3 install -e .
pip3 install -r requirements.txt
sudo reboot