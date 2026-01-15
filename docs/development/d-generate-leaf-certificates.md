# Generating Leaf Certificates

## Overview

On previous section [Bootstrapping the Root Certificate using Step CA](./b-bootstraping-ca.md), we already:
* ✅ Step CA is running
* ✅ Root CA is trusted system-wide
* ✅ Ready to issue unlimited certificates

## SaaS Side Certificate

To generate a leaf certificate for the SaaS side (`ca.saas.test`) from the running Step CA:

Install Step CLI (if not already). Refer to https://smallstep.com/docs/step-cli/installation/.

```bash
# Linux binaries install
curl -LO https://github.com/smallstep/cli/releases/download/v0.29.0/step_linux_0.29.0_amd64.tar.gz
tar -xzf step_linux_0.29.0_amd64.tar.gz
sudo mv step_0.29.0/bin/step /usr/local/bin/
rm -rf step_0.29.0
step version
```

Request the leaf certificate using the root certificates which available on `_data/step-ca/certs` directory.

```bash
mkdir -p certs
cd certs/

# copy the root_ca.crt from step-ca
cp ../_data/step-ca/certs/root_ca.crt .

step ca certificate "ca.saas.test" ca.saas.test.crt ca.saas.test.key \
  --ca-url "https://ca.saas.test:9000" \
  --root root_ca.crt

# or wildcard
step ca certificate "*.saas.test" wildcard-saas.test.crt wildcard-saas.test.key \
  --ca-url "https://ca.saas.test:9000" \
  --root root_ca.crt
```

### Use in Caddy

Create a full-chain for Caddy
```bash
cat wildcard-saas.test.crt root_ca.crt > wildcard-saas.test-full.crt
```

Example use in Caddyfile
```
some-backend.saas.test {
    tls /certs/saas.test-wildcard-full.crt /certs/saas.test-wildcard.key
    respond "HTTPS OK"
    # reverse_proxy some-backend:port
}
```

## Tenants Certificate

TODO