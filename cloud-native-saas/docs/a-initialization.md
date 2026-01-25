# Initialization

## Install Crossplane
### Preparation

Create namespace
```bash
kubectl create ns crossplane-system
```

Setup `ghcr.io` pull secret
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_PAT \
  --docker-email=any@email.com \
  -n crossplane-system
```

Setup `docker.io` pull secret
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=docker.io \
  --docker-username=YOUR_DOCKER_USERNAME \
  --docker-password=YOUR_DOCKER_PAT \
  --docker-email=any@email.com \
  -n crossplane-system
```

### Install Upbound Crossplane

Install crossplane CLI:

```bash
curl -sL "https://raw.githubusercontent.com/crossplane/crossplane/main/install.sh" | sh
```

Install
```bash
helm upgrade --install crossplane --namespace crossplane-system oci://xpkg.upbound.io/upbound/crossplane --version 2.1.3-up.1 -f artifacts/helm-values/crossplane-values.yaml
```

## Install CloudNative PG

Install using operator manifest.
```bash
kubectl apply --server-side -f \
  https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.28/releases/cnpg-1.28.0.yaml
```

Configure RBAC to allow Crossplane manage CNPG
```bash
kubectl apply -f crossplane/rbac/allow-crossplane-manage-cnpg.yaml
```


