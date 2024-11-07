This repo contains a few alternate implementations of [https-notif draft](https://datatracker.ietf.org/doc/draft-ietf-netconf-https-notif/) 

Here we implement the https-notif collector in the following languages :
  - Python
     - Flask
     - Fast API

  - Extended implementation in C
     - libmicrohttpd

  - TBD in go
    - net/http

testing using work tool

my cpu info :
```
$ lscpu
---------------
Architecture:             x86_64
  CPU op-mode(s):         32-bit, 64-bit
  Address sizes:          39 bits physical, 48 bits virtual
  Byte Order:             Little Endian
CPU(s):                   8
  On-line CPU(s) list:    0-7
Vendor ID:                GenuineIntel
  Model name:             Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz
    CPU family:           6
    Model:                142
    Thread(s) per core:   2
    Core(s) per socket:   4
    Socket(s):            1
    Stepping:             10
    CPU max MHz:          4000.0000
    CPU min MHz:          400.0000
    BogoMIPS:             3999.93
    Flags:                fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc ar
                          t arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4
                          _1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb pti ssbd ibrs ibpb stibp tpr_shadow flexpriorit
                          y ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid mpx rdseed adx smap clflushopt intel_pt xsaveopt xsavec xgetbv1 xsaves dtherm ida arat pln pt
                          s hwp hwp_notify hwp_act_window hwp_epp vnmi md_clear flush_l1d arch_capabilities
Virtualization features:  
  Virtualization:         VT-x
Caches (sum of all):      
  L1d:                    128 KiB (4 instances)
  L1i:                    128 KiB (4 instances)
  L2:                     1 MiB (4 instances)
  L3:                     8 MiB (1 instance)
NUMA:                     
  NUMA node(s):           1
  NUMA node0 CPU(s):      0-7
Vulnerabilities:          
  Gather data sampling:   Mitigation; Microcode
  Itlb multihit:          KVM: Mitigation: VMX disabled
  L1tf:                   Mitigation; PTE Inversion; VMX conditional cache flushes, SMT vulnerable
  Mds:                    Mitigation; Clear CPU buffers; SMT vulnerable
  Meltdown:               Mitigation; PTI
  Mmio stale data:        Mitigation; Clear CPU buffers; SMT vulnerable
  Reg file data sampling: Not affected
  Retbleed:               Mitigation; IBRS
  Spec rstack overflow:   Not affected
  Spec store bypass:      Mitigation; Speculative Store Bypass disabled via prctl
  Spectre v1:             Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:             Mitigation; IBRS; IBPB conditional; STIBP conditional; RSB filling; PBRSB-eIBRS Not affected; BHI Not affected
  Srbds:                  Mitigation; Microcode
  Tsx async abort:        Not affected
```

following : Workers = 2 * number of CPU cores + 1

ame machine for client and erver, o I ill run  2 core each

running :
```
gunicorn -w 9 -b 127.0.0.1:8080 app:app n --certfile ../../certs/cert.pem --keyfile ../../certs/key.pem
```

results 

for get capabilitie:

```
 wrk -t4 -c100 -d30s https://127.0.0.1:8080/capabilities
Running 30s test @ https://127.0.0.1:8080/capabilities
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.17ms    2.17ms  17.90ms   61.85%
    Req/Sec    60.06     38.52   215.00     72.38%
  6351 requests in 30.08s, 2.39MB read
Requests/sec:    211.16
Transfer/sec:     81.45KB
```

for get capablitie ith changing header
```
$ wrk -t4 -c100 -d30s -s get_seq.lua https://127.0.0.1:8080
--------------
Running 30s test @ https://127.0.0.1:8080
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.22ms    2.27ms  40.02ms   63.29%
    Req/Sec    60.36     42.86   222.00     70.08%
  6292 requests in 30.08s, 2.28MB read
Requests/sec:    209.21
Transfer/sec:     77.70KB
```

post - xml
```
wrk -t4 -c100 -d30s -H "Content-Type: application/xml" -s post_xml.lua https://127.0.0.1:8080/relay-notification
Running 30s test @ https://127.0.0.1:8080/relay-notification
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.26ms    2.06ms  17.25ms   62.55%
    Req/Sec    62.84     40.46   242.00     71.25%
  6579 requests in 30.07s, 2.16MB read
  Non-2xx or 3xx responses: 6579
Requests/sec:    218.80
Transfer/sec:     73.72KB
```

post json

```
wrk -t4 -c100 -d30s -H "Content-Type: application/xml" -s post_json.lua https://127.0.0.1:8080/relay-notification
Running 30s test @ https://127.0.0.1:8080/relay-notification
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.18ms    2.09ms  18.00ms   64.02%
    Req/Sec    57.54     30.91   141.00     60.55%
  6506 requests in 30.08s, 2.14MB read
  Non-2xx or 3xx responses: 6506
Requests/sec:    216.29
Transfer/sec:     72.87KB
```
