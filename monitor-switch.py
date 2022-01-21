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


def switch_helper(
    monitor_inputid: int,
    monitor_busid: Optional[int],
    monitor_feature: Optional[int]
):
    command = 'ddcutil'
    if monitor_busid:
        command += ' --bus={}'.format(monitor_busid)

    if monitor_feature:
        command += ' setvcp {}'.format(monitor_feature)
    else:
        command += ' setvcp 60'

    command += ' 0x{}'.format(monitor_inputid)

    print('running command: {}'.format(command))
    os.system(command)


@main.command()
@click.option('--monitor_inputid', required=True, help='id of the monitor input you want to switch to')
@click.option('--monitor_inputid', required=True, help='id of the monitor input this machine is connected to')
@click.option('--monitor_busid', required=False, help='bus id of the monitor input this machine is connected to')
def switch(
    monitor_inputid: int,
    monitor_busid: Optional[int],
    monitor_feature: Optional[int],
):
    switch_helper(monitor_inputid, monitor_busid, monitor_feature)


@main.command()
def input_sources():
    result = subprocess.run(['ddcutil', 'capabilities'], stdout=subprocess.PIPE)
    str_result = result.stdout.decode('utf-8')

    if '(Input Source)' in str_result:
        left = str_result[str_result.index('(Input Source)') - 3:]
        options = left[:left.index('Feature')]
        print('Feature: ' + options)
    else:
        print('Feature: (Input Source) not found')


@main.command()
def listen():
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
@click.option('--name', required=True, help='sys_name or driver to monitor')
@click.option('--monitor_inputid', required=True, help='id of the monitor input this machine is connected to')
@click.option('--monitor_busid', required=False, help='bus id of the monitor input this machine is connected to')
@click.option('--monitor_feature', required=False, help='feature number of Input Source')
def monitor(
    name: str,
    monitor_inputid: int,
    monitor_busid: Optional[int],
    monitor_feature: Optional[int],
):
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    print('listening to usb for connect/disconnect events, ready to perform monitor input switch to {}'.format(monitor_inputid))

    for device in iter(monitor.poll, None):
        if device.action == 'add' and (name.lower() in device.sys_name.lower() or name.lower() in str(device.driver).lower()):
            print('connected:    sys_name: {}, driver: {} connected'.format(device.sys_name, device.driver))
            switch_helper(monitor_inputid, monitor_busid, monitor_feature)
            print('listening to usb for connect/disconnect events, ready to perform monitor input switch to {}'.format(monitor_inputid))


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
