# Setting Up Local DNS

This guide describes the architecture and concept for setting up local DNS + trusted HTTPS for any local Kubernetes cluster (k3s, kind, k3d) using a single private Certificate Authority (CA).

Instead of ad-hoc certificates (mkcert, self-signed per service), we use Step CA to:
- Create one trusted root CA
- Issue multiple TLS certificates automatically
- Reuse the same trust chain across:
  - Kubernetes Ingress
  - Reverse proxies
  - Local development tools
  - Browsers on Windows/macOS/Linux

## Run The Services

Start the services using `docker compose up`.
```bash
sudo docker compose up -d
```

Check the services
```bash
sudo docker compose ps
NAME                IMAGE                            COMMAND                  SERVICE             CREATED          STATUS                             PORTS
pdns-mariadb        mariadb:lts-ubi                  "docker-entrypoint.s…"   mariadb             13 seconds ago   Up 12 seconds (health: starting)   3306/tcp
pdns-mysql-master   pschiffe/pdns-mysql:5.0-alpine   "/docker-entrypoint.…"   pdns-mysql-master   13 seconds ago   Up 11 seconds (health: starting)   0.0.0.0:53->53/tcp, :::53->53/tcp, 0.0.0.0:8081->8081/tcp, 0.0.0.0:53->53/udp, :::8081->8081/tcp, :::53->53/udp
step-ca             smallstep/step-ca:latest         "/bin/bash /entrypoi…"   step-ca             25 minutes ago   Up 15 minutes (unhealthy)          0.0.0.0:9000->9000/tcp, :::9000->9000/tcp
```

Check Step CA health:
```bash
curl -k https://localhost:9000/health
```

Expected output:
```json
{"status":"ok"}
```

## Setting Up PowerDNS
Assumptions (adjust if needed):
- Zone: saas.test
- Authoritative server container IP: 172.30.0.20

### Get into pdns container shell
```bash
sudo docker exec -it pdns-mysql-master sh
```

```bash
# List all zones
pdnsutil list-all-zones
# Delete existing zone (if exists)
pdnsutil delete-zone saas.test
# Add zone
pdnsutil create-zone saas.test
# Update SOA
pdnsutil replace-rrset saas.test saas.test SOA "ns1.saas.test. hostmaster.saas.test. 1 10800 3600 604800 3600"

pdnsutil add-record saas.test saas.test NS ns1.saas.test.

pdnsutil add-record saas.test ns1.saas.test A 172.30.0.20

# Check zone
pdnsutil check-zone saas.test
# Should output:
# Checked 3 records of 'saas.test', 0 errors, 0 warnings.
```

Add Step CA record to PowerDNS.
```
# List added zone
pdnsutil list-zone saas.test
# Add record
pdnsutil add-record saas.test ca.saas.test A 192.168.1.7
# Delete record if needed
pdnsutil delete-rrset saas.test ca.saas.test A
# Replace record with new IP
pdnsutil replace-rrset saas.test ca.saas.test A 192.168.1.3
```

Now Step CA can be accessed with valid HTTPS on https://ca.saas.test:9000.



This mirrors how HTTPS works in real production environments.

* **PowerDNS** – authoritative DNS (`*.saas.test`)
* **ExternalDNS (RFC2136)** – automatic DNS records from Kubernetes
* **Caddy**
* **Windows/macOS/Linux compatible**


## Note on WSL

Need to disable generateHosts and generateResolvConf
```bash
# /etc/wsl.conf
[network]
generateHosts=false
generateResolvConf=false
```

Need to update `.wslconfig`.
```bash
# .wslconfig
# Settings apply across all Linux distros running on WSL 2
[wsl2]
# Limits VM memory to use no more than X GB, this can be set as whole numbers using GB or MB
memory=18GB
# Turn on default connection to bind WSL 2 localhost to Windows localhost. Setting is ignored when networkingMode=mirrored
localhostforwarding=true
# Available values are: none, nat, bridged (deprecated), mirrored, and virtioproxy.
networkingMode=mirrored
# Changes how DNS requests are proxied from WSL to Windows
dnsTunneling=false

[experimental]
# Available values are: disabled, gradual, and dropCache. If the value is disabled, WSL automatic memory reclamation will be disabled. If the value is gradual, cached memory will be reclaimed slowly and automatically. If the value is dropCache or an unknown value, cached memory will be reclaimed immediately.
autoMemoryReclaim=gradual
# Only applicable when wsl2.networkingMode is set to mirrored. Specifies which ports Linux applications can bind to, even if that port is used in Windows. This enables applications to listen on a port for traffic purely within Linux, so those applications are not blocked even when that port is used for other purposes on Windows. For example, WSL will allow binding to port 53 in Linux for Docker Desktop, as it is listening only to requests from within the Linux container. Should be formatted in a comma separated list, e.g: 3000,9000,9090
ignoredPorts=53
# Only applicable when wsl2.networkingMode is set to mirrored. When set to true, will allow the Container to connect to the Host, or the Host to connect to the Container, by an IP address that's assigned to the Host. The 127.0.0.1 loopback address can always be used,this option allows for all additionally assigned local IP addresses to be used as well. Only IPv4 addresses assigned to the host are supported.
hostAddressLoopback=true
```

Restart the WSL using PowerShell as administrator:
```ps
wsl --shutdown
wsl
```
