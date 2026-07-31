# Wazuh SIEM Setup

The Wazuh SIEM is run as a VM in Proxmox

## Hypervisor and VM

Proxmox 9.2.3 is used with kernel:
Linux pve-prod-2 7.0.12-1-pve #1 SMP PREEMPT_DYNAMIC PMX 7.0.12-1 (2026-06-09T21:07Z) x86_64 GNU/Linux

The VM on which the Wazuh SIEM is installed is an Ubuntu 26.04 LTS with kernel:
Linux wazuh-test 7.0.0-28-generic #28-Ubuntu SMP PREEMPT_DYNAMIC Sun Jun 21 01:01:36 UTC 2026 x86_64 GNU/Linux

The VM was installed from the Ubuntu 26.04 LTS ISO (ubuntu-26.04-live-server-amd46.iso) with filehash:
SHA2-256(ubuntu-26.04-live-server-amd64.iso)= dec49008a71f6098d0bcfc822021f4d042d5f2db279e4d75bdd981304f1ca5d9

After installation, a `sudo apt update && sudo apt upgrade -y` command was run.

## Wazuh SIEM

The Wazuh Server is installed by following the documentation. Ref: https://documentation.wazuh.com/current/quickstart.html

`curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh && sudo bash ./wazuh-install.sh -a`

Once installed, the details of the installation are:

- WebUI -> Dashboard Management - About: `App version: 4.14.7`
- Wazuh Server: `sudo /var/ossec/bin/wazuh-control info`
  WAZUH_VERSION="v4.14.7"
  WAZUH_REVISION="rc1"
  WAZUH_TYPE="server"
- Wazuh Dashboard: `dpkg -l | grep wazuh-dashboard`
  wazuh-dashboard 4.14.7-1
- Indexer: `curl -X GET "https://localhost:9200" -u admin:<redacted> -k`
  {
  "name" : "node-1",
  "cluster_name" : "wazuh-cluster",
  "cluster_uuid" : "_zjNYWFNQQq5d8GtR-O3MA",
  "version" : {
  "number" : "7.10.2",
  "build_type" : "deb",
  "build_hash" : "2dee7e9c22f8de94b259b6ab2cc26b47cfa424f6",
  "build_date" : "2026-07-10T09:18:20.444269609Z",
  "build_snapshot" : false,
  "lucene_version" : "9.12.3",
  "minimum_wire_compatibility_version" : "7.10.0",
  "minimum_index_compatibility_version" : "7.0.0"
  },
  "tagline" : "The OpenSearch Project: https://opensearch.org/"
  }

### Configuring Wazuh Manager for Ingestion of Logs

```bash
zerodave@wazuh-test:~$ sudo cp /var/ossec/etc/ossec.conf /var/ossec/etc/ossec.conf.bk
zerodave@wazuh-test:~$ sudo vim /var/ossec/etc/ossec.conf
zerodave@wazuh-test:~$ sudo systemctl start wazuh-agent
```

`vim` was used to edit the file to remove all `<locafile>` blocks and replace them with:

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/sysmon/*.jsonl</location>
</localfile>
```

`/var/log/sysmon/` is the directory where I will place the .jsonl logs, by having a wildcard, the whole directory is under watch so any JSONL file dropped there will be indexed. The directory was created in the wazuh-server with `mkdir /var/log/sysmon`.

Also, the `<global>` configuration was changed to log all events, not just alerts:

```xml
<global>
  <logall>yes</logall>
  <logall_json>yes</logall_json
</global>
```

Next, the `filebeat.yml` config file was edited to allow for archives (all logs that don't create an alert). `sudo vim /etc/filebeat/filebeat.yml`:

```yaml
filebeat.modules:
  - module: wazuh
    alerts:
      enabled: true
    archives:
      enabled: true
```

The services were restarted:

```bash
sudo systemctl restart filebeat
sudo systemctl restart wazuh-manager
```

Finally, the `wazuh-archives-*` index pattern has to be created in the dashboard.

- Dashboard -> Dashboard Management → Index Patterns → Create index pattern
- Name: wazuh-archives-*
- Time field: `timestamp`

### Troubleshooting

1. After adding the path to the JSONL file for ingestion, there was an issue where only new logs would get scanned and indexed. Config: `/var/ossec/etc/ossec.conf`

```xml
<localfile>
  <location>/var/log/sysmon/*.jsonl</location>
  <log_format>json</log_format>
</localfile>
```

2. Wazuh was successfully detecting the JSONL file and analysing it, but no logs were being fed to Wazuh Archives:

```bash
grep -i "jsonl\|localfile" /var/ossec/logs/ossec.log
```

```
New file that matches the '/var/log/sysmon/*.jsonl' pattern
Analyzing file: '/var/log/sysmon/tst.jsonl'
```

3. After that I verified that JSONL was valid with `jq` returning no issues:

```bash
head -1 /var/log/sysmon/tst.jsonl | jq .
```

4. Performing tests for the ingestion and appending a new event to the file the event showed in `/var/ossec/logs/archives/archives.json`:

```bash
echo '{"message":"wazuh_test"}' >> /var/log/sysmon/tst.jsonl
```

6. Copying or moving the file wouldn't change the behaviour. As Wazuh detected the new file, but only ingested lines added after discovery.

7. The problem seems to have been offset tracking. Wazuh only ingests logs that change the status of the file after it being tracked. So when a file was created with `n` number of lines of JSONL, the tracker's offset was configured with an `n` value. I edited the file `file_status.json`, and changed the tracking offset of a test JSONL file to `"0"`.

```
sudo vim /var/ossec/queue/logcollector/file_status.json
```

8. After restaring wazuh-manager all logs for that file were ingested to the archives.:

```bash
systemctl restart wazuh-manager
```

NOTE: At some point during troubleshooting I checked whether permissions to the path and files were an issue. As a result, the directory being tracked now is `/home/zerodave/sysmon/*.jsonl`, not `/var/log/sysmon/*.jsonl`

### How does this affect testing?

It will be a bit of a longer process but an empty .JSONL file will be created, and the bening logs will be fed first, performing part 1 of 2 for targeted testing.

--- STill under work I think i will add a custom datafield: `{"log_sample": "benign"}` or `{"log_sample: "sample_A_aabbccdd}` so I can track everything in one go.
