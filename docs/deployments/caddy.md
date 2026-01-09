# Configure Local Caddy Server

## Installation

Install dependencies:
```bash
sudo apt-get install libnss3-tools -y
```

## Run Caddy Locally

First, make sure Caddyfile formatted correctly:
```bash
caddy fmt --overwrite --config Caddyfile.local
```

```bash
sudo caddy start --config Caddyfile.local
```


## Trusting Local Certificates

Copy the root CA into system trust. In Ubuntu installation, the root CA is located on `/root/.local/share/caddy/pki/authorities/local/root.crt`
```bash
sudo cp /root/.local/share/caddy/pki/authorities/local/root.crt \
  /usr/local/share/ca-certificates/caddy-local.crt
```

The filename must end with `.crt`.

Update trust store
```bash
sudo update-ca-certificates
```

You should now see something like:
```bash
1 added, 0 removed
```

For WSL user, you can copy the `/root/.local/share/caddy/pki/authorities/local/root.crt` into Windows directory and install the certificate as Trusted Root Certificate.
