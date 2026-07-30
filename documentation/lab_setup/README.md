## Structure

1. [Sandbox Setup](./sandbox_setup.md): details the lab setup from VM configuration and setup to tools used (Sysmon, NXLog, etc)
2. [Hardening the VM to prevent sandbox/VM detection](./VM_hardening.md): covers exctracting real values from a desktop computer, using VBoxManage to register those values in the VM's information, disabling Windows Defender, running VBoxCloak to perform further hardening as well as some manual steps, and finally running `pafish` and `al-kasher` to confirm that the actions have taken effect and the machine is as hardened as it can be.
3. [Sandbox Network and INetSim](./sandbox_network_and_inetsim.md): details how the isolated network was configured as well as the configuration required for INetSim and some troubleshooting of unexpected issues.
