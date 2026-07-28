## Structure

1. [Sandbox Setup](./sandbox_setup.md): details the lab setup from VM configuration and setup to tools used (Sysmon, NXLog, etc)
2. [Benign Log Collection](./benign_log_collection.md): covers the actions taken during the benign collection process and the idea of having Windows Defender enabled to ensure no malicious behaviour was logged.
3. [Hardening the VM to prevent sandbox/VM detection](./VBoxManage-and-VBoxCloack.md): covers exctracting real values from a desktop computer, using VBoxManage to register those values in the VM's information, disabling Windows Defender, running VBoxCloak to perform further hardening as well as some manual steps, and finally running `pafish` and `al-kasher` to confirm that the actions have taken effect and the machine is as hardened as it can be.
