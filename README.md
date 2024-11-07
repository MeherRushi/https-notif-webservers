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

running Flak:
```
gunicorn -w 5 --certfile=../../certs/server.crt --keyfile=../../certs/server.key -b 127.0.0.1:4433 app:app```

results 

for get capabilitie:

```
$ go-wrk -no-vr -c 100 -d 30 -cpus 2 https://localhost:4433/capabilities
---------------
Running 30s test @ https://localhost:4433/capabilities
  100 goroutine(s) running concurrently
22081 requests in 30.079141505s, 7.56MB read
Requests/sec:		734.10
Transfer/sec:		257.36KB
Overall Requests/sec:	730.99
Overall Transfer/sec:	256.27KB
Fastest Request:	17.969ms
Avg Req Time:		136.221ms
Slowest Request:	192.599ms
Number of Errors:	0
10%:			42.151ms
50%:			118.883ms
75%:			119.795ms
99%:			120.323ms
99.9%:			120.359ms
99.9999%:		120.359ms
99.99999%:		120.359ms


```


post - xml
```
go-wrk -no-vr -M POST -c 100 -d 30 -cpus 2 -H "Content-Type: application/xml" -body @data.xml  https://localhost:4433/relay-notification
-------------------
Running 30s test @ https://localhost:4433/relay-notification
  100 goroutine(s) running concurrently
20715 requests in 30.085145174s, 1.92MB read
Requests/sec:		688.55
Transfer/sec:		65.22KB
Overall Requests/sec:	685.52
Overall Transfer/sec:	64.94KB
Fastest Request:	22.285ms
Avg Req Time:		145.233ms
Slowest Request:	223.743ms
Number of Errors:	0
10%:			48.553ms
50%:			126.843ms
75%:			127.655ms
99%:			128.007ms
99.9%:			128.019ms
99.9999%:		128.019ms
99.99999%:		128.019ms
stddev:			18.36ms


```

post json

```
go-wrk -no-vr -M POST -c 100 -d 30 -cpus 2 -H "Content-Type: application/json" -body @data.json  https://localhost:4433/relay-notification
-------------
Running 30s test @ https://localhost:4433/relay-notification
  100 goroutine(s) running concurrently
21745 requests in 30.066116623s, 2.01MB read
Requests/sec:		723.24
Transfer/sec:		68.51KB
Overall Requests/sec:	720.16
Overall Transfer/sec:	68.22KB
Fastest Request:	37.54ms
Avg Req Time:		138.266ms
Slowest Request:	170.639ms
Number of Errors:	0
10%:			62.113ms
50%:			125.123ms
75%:			125.771ms
99%:			126.087ms
99.9%:			126.095ms
99.9999%:		126.095ms
99.99999%:		126.095ms
stddev:			9.575ms

```


-------------------------------------
running fast_Api

```
gunicorn -w 5 --certfile=../../certs/server.crt --keyfile=../../certs/server.key -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:4433
```


for get capabilitie:

```
$ go-wrk -no-vr -c 100 -d 30 -cpus 2 https://localhost:4433/capabilities
---------------
Running 30s test @ https://localhost:4433/capabilities
  100 goroutine(s) running concurrently
188870 requests in 29.995154664s, 100.15MB read
Requests/sec:		6296.68
Transfer/sec:		3.34MB
Overall Requests/sec:	6270.42
Overall Transfer/sec:	3.32MB
Fastest Request:	2.284ms
Avg Req Time:		15.88ms
Slowest Request:	96.843ms
Number of Errors:	0
10%:			5.814ms
50%:			6.951ms
75%:			7.253ms
99%:			7.446ms
99.9%:			7.451ms
99.9999%:		7.452ms
99.99999%:		7.452ms
stddev:			5.667ms
```

post - xml
```
go-wrk -no-vr -M POST -c 100 -d 30 -cpus 2 -H "Content-Type: application/xml" -body @data.xml  https://localhost:4433/relay-notification
-------------------

Running 30s test @ https://localhost:4433/relay-notification
  100 goroutine(s) running concurrently
147359 requests in 29.999537057s, 7.87MB read
Requests/sec:		4912.04
Transfer/sec:		268.63KB
Overall Requests/sec:	4893.13
Overall Transfer/sec:	267.59KB
Fastest Request:	2.971ms
Avg Req Time:		20.357ms
Slowest Request:	138.543ms
Number of Errors:	0
10%:			5.571ms
50%:			5.899ms
75%:			6.247ms
99%:			6.48ms
99.9%:			6.488ms
99.9999%:		6.489ms
99.99999%:		6.489ms
stddev:			10.694ms



```

post json

```
go-wrk -no-vr -M POST -c 100 -d 30 -cpus 2 -H "Content-Type: application/json" -body @data.json  https://localhost:4433/relay-notification
-------------
Running 30s test @ https://localhost:4433/relay-notification
  100 goroutine(s) running concurrently
167312 requests in 29.996081982s, 8.94MB read
Requests/sec:		5577.80
Transfer/sec:		305.04KB
Overall Requests/sec:	5550.49
Overall Transfer/sec:	303.54KB
Fastest Request:	1.183ms
Avg Req Time:		17.927ms
Slowest Request:	106.155ms
Number of Errors:	0
10%:			5.061ms
50%:			5.915ms
75%:			6.166ms
99%:			6.348ms
99.9%:			6.358ms
99.9999%:		6.359ms
99.99999%:		6.359ms
stddev:			8.516ms


```