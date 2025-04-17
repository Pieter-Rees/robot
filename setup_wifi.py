#!/usr/bin/env python3

import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        sys.exit(1)

def install_packages():
    print("Installing required packages...")
    packages = [
        "hostapd",
        "dnsmasq",
        "netfilter-persistent",
        "iptables-persistent"
    ]
    run_command(f"sudo apt-get update")
    run_command(f"sudo apt-get install -y {' '.join(packages)}")

def configure_network():
    print("Configuring network interface...")
    
    # Backup existing dhcpcd.conf
    run_command("sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bak")
    
    # Add static IP configuration
    with open("/etc/dhcpcd.conf", "a") as f:
        f.write("\n# Static IP configuration for AP mode\n")
        f.write("interface wlan0\n")
        f.write("static ip_address=192.168.4.1/24\n")
        f.write("nohook wpa_supplicant\n")

def configure_hostapd():
    print("Configuring hostapd...")
    
    # Create hostapd configuration
    hostapd_conf = """interface=wlan0
driver=nl80211
ssid=RobotAP
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=robot1234
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
    
    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write(hostapd_conf)
    
    # Update hostapd configuration file path
    run_command('sudo sed -i "s/#DAEMON_CONF=\"\"/DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"/" /etc/default/hostapd')

def configure_dnsmasq():
    print("Configuring dnsmasq...")
    
    # Backup existing dnsmasq.conf
    run_command("sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.bak")
    
    # Create dnsmasq configuration
    dnsmasq_conf = """interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
"""
    
    with open("/etc/dnsmasq.conf", "w") as f:
        f.write(dnsmasq_conf)

def enable_services():
    print("Enabling services...")
    services = ["hostapd", "dnsmasq"]
    for service in services:
        run_command(f"sudo systemctl unmask {service}")
        run_command(f"sudo systemctl enable {service}")
        run_command(f"sudo systemctl start {service}")

def main():
    if os.geteuid() != 0:
        print("This script must be run as root. Please use sudo.")
        sys.exit(1)
    
    print("Setting up WiFi access point...")
    install_packages()
    configure_network()
    configure_hostapd()
    configure_dnsmasq()
    enable_services()
    
    print("\nSetup complete!")
    print("WiFi network details:")
    print("SSID: RobotAP")
    print("Password: robot1234")
    print("IP address: 192.168.4.1")
    print("\nPlease reboot your Raspberry Pi for changes to take effect.")

if __name__ == "__main__":
    main() 