# Ollama Host: Hardware and Software Information

## Software
### OS
```bash
$ cat /etc/os-release
NAME="Arch Linux"
PRETTY_NAME="Arch Linux"
ID=arch
BUILD_ID=rolling
ANSI_COLOR="38;2;23;147;209"
HOME_URL="https://archlinux.org/"
DOCUMENTATION_URL="https://wiki.archlinux.org/"
SUPPORT_URL="https://bbs.archlinux.org/"
BUG_REPORT_URL="https://gitlab.archlinux.org/groups/archlinux/-/issues"
PRIVACY_POLICY_URL="https://terms.archlinux.org/docs/privacy-policy/"
LOGO=archlinux-logo
```
### Kernel
```bash
$ uname -a
Linux zero-arch 7.1.4-arch1-1 #1 SMP PREEMPT_DYNAMIC Sat, 18 Jul 2026 17:30:57 +0000 x86_64 GNU/Linux
```
### Hostname
```bash
$ hostnamectl
  Static hostname: zero-arch
        Icon name: computer-desktop
          Chassis: desktop 🖥️
Chassis Asset Tag: To be filled by O.E.M.
       Machine ID: 7eed611ce99f4236a0aef9baedd4f325
          Boot ID: 6e22df92786c45f99b980c906ab6920c
 Operating System: Arch Linux
           Kernel: Linux 7.1.4-arch1-1
     Architecture: x86-64
  Hardware Vendor: Micro-Star International Co., Ltd.
   Hardware Model: MS-7E62
 Hardware Version: 2.0
 Firmware Version: 2.A4C
    Firmware Date: Thu 2026-01-08
     Firmware Age: 6month 3w 3d
```


## Hardware
### CPU
```bash
$ lscpu
Architecture:                x86_64
  CPU op-mode(s):            32-bit, 64-bit
  Address sizes:             48 bits physical, 48 bits virtual
  Byte Order:                Little Endian
CPU(s):                      24
  On-line CPU(s) list:       0-23
Vendor ID:                   AuthenticAMD
  Model name:                AMD Ryzen 9 9900X 12-Core Processor
    CPU family:              26
    Model:                   68
    Thread(s) per core:      2
    Core(s) per socket:      12
    Socket(s):               1
    Stepping:                0
    Microcode version:       0xb404035
    Frequency boost:         enabled
    CPU(s) scaling MHz:      25%
    CPU max MHz:             5662.0161
    CPU min MHz:             613.9540
    BogoMIPS:                8799.98
    Flags:                   fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdt
                             scp lm constant_tsc rep_good amd_lbr_v2 nopl xtopology nonstop_tsc cpuid extd_apicid aperfmperf rapl pni pclmulqdq monitor ssse3 fma cx16 s
                             se4_1 sse4_2 movbe popcnt aes xsave avx f16c rdrand lahf_lm cmp_legacy svm extapic cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw ibs
                             skinit wdt tce topoext perfctr_core perfctr_nb bpext perfctr_llc mwaitx cpuid_fault cpb cat_l3 cdp_l3 hw_pstate ssbd mba perfmon_v2 ibrs ib
                             pb stibp ibrs_enhanced vmmcall fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm rdt_a avx512f avx512dq rdseed adx smap avx512ifma c
                             lflushopt clwb avx512cd sha_ni avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local user_shst
                             k avx_vnni avx512_bf16 clzero irperf xsaveerptr rdpru wbnoinvd cppc arat npt lbrv svm_lock nrip_save tsc_scale vmcb_clean flushbyasid decod
                             eassists pausefilter pfthreshold avic v_vmsave_vmload vgif x2avic v_spec_ctrl vnmi avx512vbmi umip pku ospke avx512_vbmi2 gfni vaes vpclmul
                             qdq avx512_vnni avx512_bitalg avx512_vpopcntdq rdpid bus_lock_detect movdiri movdir64b overflow_recov succor smca fsrm avx512_vp2intersect
                             flush_l1d amd_lbr_pmc_freeze
Virtualization features:
  Virtualization:            AMD-V
Caches (sum of all):
  L1d:                       576 KiB (12 instances)
  L1i:                       384 KiB (12 instances)
  L2:                        12 MiB (12 instances)
  L3:                        64 MiB (2 instances)
NUMA:
  NUMA node(s):              1
  NUMA node0 CPU(s):         0-23
Vulnerabilities:
  Gather data sampling:      Not affected
  Ghostwrite:                Not affected
  Indirect target selection: Not affected
  Itlb multihit:             Not affected
  L1tf:                      Not affected
  Mds:                       Not affected
  Meltdown:                  Not affected
  Mmio stale data:           Not affected
  Old microcode:             Not affected
  Reg file data sampling:    Not affected
  Retbleed:                  Not affected
  Spec rstack overflow:      Mitigation; IBPB on VMEXIT only
  Spec store bypass:         Mitigation; Speculative Store Bypass disabled via prctl
  Spectre v1:                Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:                Mitigation; Enhanced / Automatic IBRS; IBPB conditional; STIBP always-on; PBRSB-eIBRS Not affected; BHI Not affected
  Srbds:                     Not affected
  Tsa:                       Not affected
  Tsx async abort:           Not affected
  Vmscape:                   Mitigation; IBPB on VMEXIT
```

### RAM
```bash
free -h
               total        used        free      shared  buff/cache   available
Mem:            60Gi        11Gi        39Gi        37Mi        10Gi        48Gi
Swap:          8.0Gi          0B       8.0Gi
```
### Storage
```bash
$ lsblk
NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
nvme0n1     259:0    0  1.8T  0 disk
├─nvme0n1p1 259:1    0    1G  0 part /boot
└─nvme0n1p2 259:2    0  1.8T  0 part /
```
```bash
$ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  1.8T  333G  1.4T  20% /
devtmpfs         31G     0   31G   0% /dev
tmpfs            31G   33M   31G   1% /dev/shm
efivarfs        256K   70K  182K  28% /sys/firmware/efi/efivars
tmpfs            13G  1.7M   13G   1% /run
none            1.0M     0  1.0M   0% /run/credentials/systemd-journald.service
tmpfs            31G  356K   31G   1% /tmp
/dev/nvme0n1p1 1022M   64M  959M   7% /boot
none            1.0M     0  1.0M   0% /run/credentials/getty@tty1.service
tmpfs           6.1G  204K  6.1G   1% /run/user/1000
```
### GPU
```bash
$ lspci -k | grep -EA3 'VGA|3D'
03:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Navi 48 [Radeon RX 9070/9070 XT/9070 GRE] (rev c3)
        Subsystem: ASUSTeK Computer Inc. Device 0618
        Kernel driver in use: amdgpu
        Kernel modules: amdgpu
--
0c:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Granite Ridge [Radeon Graphics] (rev c2)
        Subsystem: Micro-Star International Co., Ltd. [MSI] Device 7e62
        Kernel driver in use: amdgpu
        Kernel modules: amdgpu
```

```bash
$ rocminfo | grep -i "Marketing Name"
  Marketing Name:          AMD Ryzen 9 9900X 12-Core Processor
  Marketing Name:          AMD Radeon RX 9070
  Marketing Name:          AMD Ryzen 9 9900X 12-Core Processor
```

```bash
$ rocm-smi

========================================== ROCm System Management Interface ==========================================
==================================================== Concise Info ====================================================
Device  Node  IDs              Temp    Power   Partitions          SCLK     MCLK     Fan  Perf  PwrCap  VRAM%  GPU%
              (DID,     GUID)  (Edge)  (Avg)   (Mem, Compute, ID)
======================================================================================================================
0       1     0x7550,   58314  57.0°C  148.0W  N/A, N/A, 0         1143Mhz  772Mhz   0%   auto  230.0W  59%    8%
1       2     0x13c0,   38164  40.0°C  0.006W  N/A, N/A, 0         N/A      2400Mhz  0%   auto  N/A     0%     0%
======================================================================================================================
================================================ End of ROCm SMI Log =================================================
```

```bash
rocm-smi --showproductname
============================ ROCm System Management Interface ============================
WARNING: AMD GPU device(s) is/are in a low-power state. Check power control/runtime_status

====================================== Product Info ======================================
GPU[0]          : Card Series:          AMD Radeon RX 9070
GPU[0]          : Card Model:           0x7550
GPU[0]          : Card Vendor:          Advanced Micro Devices, Inc. [AMD/ATI]
GPU[0]          : Card SKU:             G295BP0
GPU[0]          : Subsystem ID:         0x0618
GPU[0]          : Device Rev:           0xc3
GPU[0]          : Node ID:              1
GPU[0]          : GUID:                 58314
GPU[0]          : GFX Version:          gfx1201
GPU[1]          : Card Series:          AMD Ryzen 9 9900X 12-Core Processor
GPU[1]          : Card Model:           0x13c0
GPU[1]          : Card Vendor:          Advanced Micro Devices, Inc. [AMD/ATI]
GPU[1]          : Card SKU:             RAPHAEL
GPU[1]          : Subsystem ID:         0x7e62
GPU[1]          : Device Rev:           0xc2
GPU[1]          : Node ID:              2
GPU[1]          : GUID:                 38164
GPU[1]          : GFX Version:          gfx1036
==========================================================================================
================================== End of ROCm SMI Log ===================================
```
