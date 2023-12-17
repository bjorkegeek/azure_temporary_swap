# azure_temporary_swap
For linux VMs running under Azure - detect temporary disks and turn them into
swap

## Installation

```sh
# Download the script that does the heavy lifting
wget -O /usr/local/sbin/azure_temporary_swap.py https://raw.githubusercontent.com/bjorkegeek/azure_temporary_swap/main/azure_temporary_swap.py

# Download systemd service file
wget -O /etc/systemd/system/azure_temporary_swap.service https://raw.githubusercontent.com/bjorkegeek/azure_temporary_swap/main/azure_temporary_swap.service

# Get the service running
systemctl daemon-reload
systemctl enable --now azure_temporary_swap.py
```

## How It Works

This script is designed for VMs running on Azure that have access to a temporary disk. These temporary disks are unique in that they do not retain data when the VM is re-provisioned. A practical use for these ephemeral storage resources under Linux is to convert them into swap devices. This approach allows for more efficient memory management; data that is infrequently accessed can be moved to swap space, freeing up RAM for more critical tasks like disk caching.
Process Overview

1. Identification of Temporary Disks: The script uses `blkid` to identify any 
available temporary disks. These are typically presented as NTFS volumes by 
Azure.

2. Swap Space Initialization: It then proceeds to format the entire identified 
disk as swap space using `mkswap`. This step is crucial for preparing the disk 
for use as a virtual memory extension.

3. Activation of Swap Partitions: Finally, the script activates any swap
partitions that are not already in use. This includes re-activating swap spaces
after a VM reboot, assuming they were previously set up.

## Credits

Written by David Björkevik, paid for by Envista AB.