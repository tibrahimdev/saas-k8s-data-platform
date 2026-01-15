# Bootstrapping the Root Certificate using Step CA

In this section, we set up **Step CA** as a **local private Certificate Authority (CA)** and establish trust on the host machine.

By the end of this section:

* Step CA is running locally
* A **single root CA** is created
* The root CA is trusted by the OS and browser
* Any certificate issued by Step CA is trusted automatically

## Architecture Overview

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │ trusts
┌──────▼───────┐
│   Step CA    │  ← Root CA
└──────┬───────┘
       │ issues certs
┌──────▼─────────────┐
│ Caddy / Ingress    │
└────────────────────┘
```

> ⚠️ Important:
> **You only install trust once** (the root CA).
> All future TLS certificates are accepted automatically.

## Prerequisites
- Docker + Docker Compose

## Step 1 — Create Step CA Data Directory and Password

Create a working directory:
```bash
# ! _data directory is ignored by .gitignore
mkdir -p _data/step-ca/secrets
```

Create step-ca password file. Change the password as you need.
```bash
# Create the password file
echo "password" > _data/step-ca/secrets/password
```

Update directory ownership
```bash
sudo chown -R 1000:1000 _data/step-ca
```

## Step 2 — Initialize the Certificate Authority
We run Step CA as a **Docker container**, so it is:

* Easy to reset
* Isolated
* Identical across OSes

We will initialize Step CA **inside the container**.

Run:
```bash
sudo docker compose run --rm step-ca step ca init
```

You will be given some prompts. Use following table as references

| Prompt | Example value |
| --- | --- |
| Deployment Type | Standalone |
| What would you like to name your new PKI? | saas-local-ca |
| What DNS names or IP addresses will clients use to reach your CA? | step-ca.saas.test |
| What IP and port will your new CA bind to? (:443 will bind to 0.0.0.0:443) | :9000 |
| What would you like to name the CA's first provisioner | admin |
| Choose a password for your CA keys and first provisioner | your-password-created-in-step-1 |


This command generates:
- Root certificate: /home/step/certs/root_ca.crt
- Root private key: /home/step/secrets/root_ca_key
- Root fingerprint: 
- Intermediate certificate: /home/step/certs/intermediate_ca.crt
- Intermediate private key: /home/step/secrets/intermediate_ca_key
- Database folder: /home/step/db
- Default configuration: /home/step/config/defaults.json
- Certificate Authority configuration: /home/step/config/ca.json

All data is stored in `_data/step-ca` directory.
```bash
_data/
└── step-ca
    ├── certs
    │   ├── intermediate_ca.crt
    │   └── root_ca.crt
    ├── config
    │   ├── ca.json
    │   └── defaults.json
    ├── db
    │   ├── 000000.vlog
    │   ├── 000002.sst
    │   ├── KEYREGISTRY
    │   └── MANIFEST
    ├── secrets
    │   ├── intermediate_ca_key
    │   ├── password
    │   └── root_ca_key
    └── templates
```

## Step 3 — Extract the Root CA Certificate

The root certificate must be installed on your machine.

Copy it out of the container volume data:

```bash
ls _data/step-ca/certs/
```

You should see something like:

```
intermediate_ca.crt  root_ca.crt
```

We will install **only the root CA**.

## Step 4 — Install Root CA into OS Trust Store

### Linux (Ubuntu / Debian)

```bash
sudo cp _data/step-ca/certs/root_ca.crt /usr/local/share/ca-certificates/saas-local-ca.crt
sudo update-ca-certificates --fresh
```

Verify:

```bash
openssl verify /usr/local/share/ca-certificates/saas-local-ca.crt
```

### macOS

```bash
sudo security add-trusted-cert \
  -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  _data/step-ca/certs/root_ca.crt
```

---

### Windows

1. Download or copy `_data/step-ca/certs/root_ca.crt` into Windows folder.
2. Double-click `root_ca.crt`
3. Install Certificate
4. Choose **Local Machine**
5. Place into **Trusted Root Certification Authorities**
6. Finish the wizard

## What We Have Now

At this point:

* ✅ Step CA is running
* ✅ Root CA is trusted system-wide
* ✅ Ready to issue unlimited certificates

## Next

➡️ **Configuring PowerDNS as the Authoritative DNS for `saas.test`**

Next, we will:

* Deploy PowerDNS
* Create the `saas.test` zone
* Prepare it for ExternalDNS (RFC2136)
