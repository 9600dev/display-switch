import os
import pyudev
import click
import subprocess
import regex
from click_help_colors import HelpColorsGroup
from typing import Optional

@click.group()
def main():
    pass


def split_callback(ctx, param, value):
    if value is not None and ', ' in value:
        return value.split(', ')
    elif value is not None and ',' in value:
        return value.split(',')
    else:
        return [value]


def switch_display(display_inputid: str, display_busid: Optional[int], display_feature: Optional[int]):
    command = 'ddcutil'
    if display_busid:
        command += f' --bus={display_busid}'

    if display_feature:
        command += f' setvcp {display_feature}'
    else:
        command += ' setvcp 60'

    command += f' 0x{display_inputid}'

    print(f'Running command: {command}')
    os.system(command)


@main.command()
@click.option('--display_inputids', required=True, type=str, callback=split_callback, help='List of input IDs of the display inputs (HDMI, DisplayPort, etc.) this computer is connected to')
@click.option('--display_busids', required=False, type=str, callback=split_callback, help='List of bus IDs for the displays')
@click.option('--display_features', required=False, type=str, callback=split_callback, help='List of feature numbers of Input Source for the displays')
def switch(
        display_inputids, 
        display_busids, 
        display_features
    ):

    # Use default values if busids or features are not provided
    default_busid = None
    default_feature = None

    # Loop through each display and switch it
    for i, inputid in enumerate(display_inputids):
        busid = display_busids[i] if display_busids else default_busid
        feature = display_features[i] if display_features else default_feature
        switch_display(inputid, busid, feature)


@main.command()
def show_display_parameters():
    # Detect all connected monitors
    detect_result = subprocess.run(['ddcutil', 'detect', '--brief'], stdout=subprocess.PIPE)
    detect_output = detect_result.stdout.decode('utf-8')

    print(detect_output)
    # Parse the output to get the bus IDs
    bus_ids = regex.findall(r'/dev/i2c-(\d+)', detect_output)

    # Iterate over each bus ID to get capabilities
    for bus_id in bus_ids:
        print(f'Bus ID: {bus_id}')
        capabilities_result = subprocess.run(['ddcutil', '--bus', bus_id, 'capabilities'], stdout=subprocess.PIPE)
        capabilities_output = capabilities_result.stdout.decode('utf-8')

        # Find the feature code for Input Source
        feature_match = regex.search(r'Feature: (\w+) \(Input Source\)', capabilities_output)
        if feature_match:
            left = capabilities_output[capabilities_output.index('(Input Source)') - 3:]
            options = left[:left.index('Feature')]
            print('Feature: ' + options)
        else:
            print('Input Source Feature ID: Not found')

        print()  # Add a newline for better readability between monitors


@main.command()
def show_usb_parameters():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    print('listening to usb for connect/disconnect events')
    for device in iter(monitor.poll, None):
        if device.action == 'add':
            print('connected:    sys_name: {}, driver: {} connected'.format(device.sys_name, device.driver))
        elif device.action == 'remove':
            print('disconnected: sys_name: {}, driver: {} disconnected'.format(device.sys_name, device.driver))



@main.command()
@click.option('--usb_sys_name', required=True, help='sys_name or usb driver to monitor')
@click.option('--display_inputids_connected', required=True, type=str, callback=split_callback, help='List of input IDs of the display inputs (HDMI, DisplayPort, etc.) this computer is connected to')
@click.option('--display_inputids_disconnected', required=False, type=str, callback=split_callback, help='List of input IDs of the display inputs (HDMI, DisplayPort, etc.) this computer is connected to')
@click.option('--display_busids', required=False, type=str, callback=split_callback, help='List of bus IDs for the displays')
@click.option('--display_features', required=False, type=str, callback=split_callback, help='List of feature numbers of Input Source for the displays')
def listen(
    usb_sys_name: str,
    display_inputids_connected: list[str],
    display_inputids_disconnected: Optional[list[str]],
    display_busids: Optional[list[str]],
    display_features: Optional[list[str]],
):
    print(f'display_inputids_connected: {display_inputids_connected}')
    if display_inputids_disconnected:
        print(f'display_inputids_disconnected: {display_inputids_disconnected}')
    print(f'display_busids: {display_busids}')
    print(f'display_features: {display_features}')

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    print('Listening to USB for connect/disconnect events, ready to perform monitor input switch.')

    for device in iter(monitor.poll, None):
        if device.action == 'add' and (usb_sys_name.lower() in device.sys_name.lower() or usb_sys_name.lower() in str(device.driver).lower()):
            print('Connected: sys_name: {}, driver: {} connected'.format(device.sys_name, device.driver))
            for i, display_inputid in enumerate(display_inputids_connected):
                display_busid = display_busids[i] if display_busids else None
                display_feature = display_features[i] if display_features else None
                switch_display(display_inputid, display_busid, display_feature)
            print('Listening to USB for connect/disconnect events, ready to perform monitor input switch.')
        elif device.action == 'remove' and display_inputids_disconnected and len(display_inputids_disconnected) > 0 and (usb_sys_name.lower() in device.sys_name.lower() or usb_sys_name.lower() in str(device.driver).lower()):
            print('Disconnected: sys_name: {}, driver: {} connected'.format(device.sys_name, device.driver))
            for i, display_inputid in enumerate(display_inputids_disconnected):
                display_busid = display_busids[i] if display_busids else None
                display_feature = display_features[i] if display_features else None
                switch_display(display_inputid, display_busid, display_feature)
            print('Listening to USB for connect/disconnect events, ready to perform monitor input switch.')


if __name__ == '__main__':
    print('Make sure you have enabled read/write access to i2c devices for users in the i2c group:')
    print()
    print('$ groupadd i2c')
    print('$ echo \'KERNEL=="i2c-[0-9]*", GROUP="i2c"\' >> /etc/udev/rules.d/10-local_i2c_group.rules')
    print('$ udevadm control --reload-rules && udevadm trigger')
    print()
    print('$ sudo usermod -aG i2c $(whoami)')
    print()
    main()
