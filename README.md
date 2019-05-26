# Home Assistant Padavan Device Tracker

This device tracker component allows you to get **wireless** devices presence from 
[Padavan](https://bitbucket.org/padavan/rt-n56u)-based routers.

Tested on Xiaomi MiWiFi Mini Router with Padavan 3.4.3.9-099_195eba6. Probably need additional changes to make it work 
on other devices.

Purpose
-------

Detect ANY Wi-Fi clients (=Android/iOS/Windows Phone smartphones...) with 100% accuracy at any time moment.

Why not ...?
------------
  
  - [Nmap](https://home-assistant.io/components/device_tracker.nmap_tracker/) - mobile devices (Nexus 5X, iPhones) can
    go to a deep sleep so nmap can send dozen different packages and get nothing. It's very unreliable. You need at 
    least 3 minutes to understand client is really offline and not ignoring your requests.
  - [OpenWrt luci](https://home-assistant.io/components/device_tracker.luci/) - can't check, but from [source code](https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/components/device_tracker/luci.py#L101)
    it checks ARP table which is totally wrong, because it doesn't remove client immediately after disconnect.
  - [OpenWrt ubus](https://home-assistant.io/components/device_tracker.ubus/) - looks promising, but doesn't exist in
    Padavan firmware out of the box.
  - [Xiaomi](https://home-assistant.io/components/device_tracker.xiaomi/) - works like this solution (=perfectly), 
    but only in _router_ mode. Padavan tracker works in AP mode too.

Installation (Xiaomi MiWiFi Mini Router only)
------------------------------------------

1. Download stock Xiaomi dev firmware http://www1.miwifi.com/miwifi_download.html.
2. Flash it via web interface.
3. Install Android app ([ru](https://4pda.ru/forum/index.php?showtopic=661224), 
[en](http://xiaomi.eu/community/threads/xiaomi-router-app-translation.25386/page-3#post-262621)).
4. Attach router to your Mi account.
5. Download ssh unlock firmware http://d.miwifi.com/rom/ssh, remember login/pass - it's ssh credentials.
6. Put it on USB FAT32 stick:
   1. Turn on Router while reset-button pressed and USB stick plugged in
   2. Release Reset-button after the orange LED starts flashing
   3. Wait a minute to complete flashing and device is online again (shown by blue LED)
7. Check SSH to your device.
8. Go to http://prometheus.freize.net/index.html:
   1. Download utility.
   2. Build Toolchain.
   3. Build Firmware.
   4. Flash Firmware.
   5. Flash EEPROM.
9. Add the following lines to the `configuration.yaml`:
   
  ```yaml
  device_tracker:
    - platform: padavan_tracker
      consider_home: 10
      interval_seconds: 3
      url: http://192.168.1.1/ # web interface url (don't forget about `/` in the end)
      username: admin # Web interface user name
      password: admin # Web interface user pass
  ```  

Notes
-----

- Sometimes/most of the time web interface will be inaccessible while this component is working. That's because Padavan firmware doesn't allow >1 users authorized from different IPs. Check the possible [workaround](https://github.com/PaulAnnekov/home-assistant-padavan-tracker/issues/8) for this.


Useful links
-------------
 
 - Firmware sources: https://bitbucket.org/padavan/rt-n56u
 - Firmware build and installation utility: http://prometheus.freize.net/index.html
 - OpenWrt wiki related to Xiaomi MiWiFi Mini: https://wiki.openwrt.org/toh/xiaomi/mini
