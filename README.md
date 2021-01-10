# temperature_sensor

This is a simple program that sends temperature sensors data to ThingSpeak backend service. I am using it at home for temperature monitoring.

# Installation steps on Raspberry PI
1. Create fresh Raspberry PI image with Imager or `dd`
1. Enable SSH access. Create /boot/ssh file on new card: `touch /Volumes/boot/ssh`
1. Create `wpa_supplicant.conf` file in `boot` directory:
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="NETWORK-NAME"
    psk="NETWORK-PASSWORD"
}
```
1. Edit `/boot/config.txt` file and add following line:
`dtoverlay=w1-gpio,gpiopin=4`
1. install w1thermsensor Python package: `sudo apt install python3-w1thermsensor`
1. Run: 
```
$ sudo modprobe w1-gpio
$ sudo modprobe w1-therm
```
1. Copy systemctl file: `sudo cp temperature.service /lib/systemd/system/temperature.service`
1. Change permissions: `sudo chmod 644 /lib/systemd/system/temperature.service`
1. Enable service
```
sudo systemctl daemon-reload
sudo systemctl enable sample.service
```
