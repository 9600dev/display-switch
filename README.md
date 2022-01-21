# Monitor Input Switcher

Allows you to switch monitor inputs from the command line, either directly, or by listening to USB connect/disconnect events

```$ python3 monitor-switch.py```
```
Make sure you have enabled read/write access to i2c devices for users in the i2c group:

$ groupadd i2c
$ echo 'KERNEL=="i2c-[0-9]*", GROUP="i2c"' >> /etc/udev/rules.d/10-local_i2c_group.rules
$ udevadm control --reload-rules && udevadm trigger

$ sudo usermod -aG i2c $(whoami)

Usage: monitor-switch.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  input-sources
  listen
  monitor
  switch
```

Example: Switch to input display "Display Port 1" when keyboard is connected:

```python3 switch.py monitor --name '1-1.3:1.2' --monitor_input 0f```