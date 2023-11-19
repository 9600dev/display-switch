# Display Input Switcher

Allows you to switch display inputs (hdmi, displayport) from the command line, either directly, or by listening to USB connect/disconnect events. Supports multiple monitors.

```$ python3 display-switch.py```
```
Make sure you have enabled read/write access to i2c devices for users in the i2c group:

$ groupadd i2c
$ echo 'KERNEL=="i2c-[0-9]*", GROUP="i2c"' >> /etc/udev/rules.d/10-local_i2c_group.rules
$ udevadm control --reload-rules && udevadm trigger

$ sudo usermod -aG i2c $(whoami)


Usage: display-switch.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  listen
  show-display-parameters
  show-usb-parameters
  switch
```

```bash
python display-switch.py show-display-parameters

Display 1
   I2C bus:          /dev/i2c-6
   DRM connector:    card0-DP-2
   Monitor:          AUS:ROG XG27UQ:LBLMQS194183

Display 2
   I2C bus:          /dev/i2c-7
   DRM connector:    card0-DP-3
   Monitor:          AUS:ROG XG27UQR:M7LMQS001163


Bus ID: 6
Feature: 60 (Input Source)
      Values:
         0f: DisplayPort-1
         10: DisplayPort-2
         11: HDMI-1
         12: HDMI-2


Bus ID: 7
Feature: 60 (Input Source)
      Values:
         0f: DisplayPort-1
         10: DisplayPort-2
         11: HDMI-1
         12: HDMI-2


```

Example: Switch both monitors to input display "DisplayPort-1" when usb hub is connected, and "DisplayPort-2" when usb hub is disconnected:

```
python display-switch.py listen --usb_sys_name 6-3 --display_inputids_connected 0f,0f --display_inputids_disconnected 10,10 --display_busids 6,7 --display_features 60,60
```

