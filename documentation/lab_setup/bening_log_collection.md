## Bening Log Collection Actions

After configuring Sysmon, NXLog, and the scripts to extract the Sysmon logs live via a serial port (COM1), 48 hours of benign logs were collected. Log collection is persistent across reboots and shutdowns. The logs are collected whilst Windows Defender is enabled and with an active network (internet) network connection. At this point, there is no malware sample downloaded to the VM; this is to emulate a realistic usage of a workstation. Defender being enabled for this part should prevent any malicious behaviour/files from creating logs, assuring that the "bening" logs (baseline) is True Positive (TP)-free.

The actions taken during those 48 hours are designed to create normal benign activity, fill the machine with realistic software to prevent sandbox detection, and there'll be instances where no actions are taken for hours. The manual actions are the following.

1. Windows Updates were run.
2. Installing, opening and using Brave Browser.
3. Install and opening Foxit Free PDF Reader.
4. Install Outlook: downloaded an .exe that failed and redirected to the Microsoft Store.
   - After opening, outlook started an update on its own.
   - Once updated, logged in to a throwaway account.
   - Downloaded a bening file from an email (threat-landscape-report-2025.pdf from Fortinet)
5. Installing Process Monitor (ProcMon), consists of downloading a .zip file and extracting `Procmon.exe`.
6. Installing Wireshark from `Wireshark-4.6.7-x64.exe` binary. Added all extensikons and installed nopcap and USBcap.
   - Rebooted right after
7. Uninstalled all Microsoft bloatware.
   - Cortana
   - Copilot
   - Maps
   - Microsoft 365 Copilot
   - \* left things like Xbox "Console Companion", "Xbox Live", "Camera", "Feedback Hub" and others for realism
8. Shutdown machine to take a Snapshot called
9. Started Wireshark packet capture on the ethernet (only) network interface. Navigated to `setu.ie`, `youtube.com`, `zerordave.com`, and `microsoft.com`. The .pcap was saved to the Desktop as `network-troubleshooting.pcap`
10. Created a `Database Passwords.txt` file and saved it to the Desktop with the following contents.

```txt
mysql: "mysqlp@ssword1234!"
user: "secretuser@mysql1234"
```

11. Installed Microsoft 365 (free with limited features) from the Microsoft Store. This executed a reboot on its own.
12. Create DOCX document from Word Invoice Template and saved the document to the Desktop as `network-equipment-invoice.docx`
13. Several reboots and normal operations occurred for the total of 48hours.
