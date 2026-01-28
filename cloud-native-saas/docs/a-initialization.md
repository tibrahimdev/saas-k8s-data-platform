# Initialization

## Install Some CLI/IDE Tools

[KCL language server](https://www.kcl-lang.io/docs/user_docs/getting-started/install#install-language-server)
```bash
wget -q https://kcl-lang.io/script/install-kcl-lsp.sh -O - | /bin/bash
```

## Install Kubevela
Due to issue with admission control webhook timeout, we will install from local chart
```bash
# Run these from root directory of this cloned repo
export DEFAULT_KUBEVELA_HELM_URI=artifacts/charts/vela-core
vela install -f $DEFAULT_KUBEVELA_HELM_URI

# Install velaux
vela addon enable velaux

# Installing addon fluxcd
vela addon enable fluxcd namespace=$SYSTEM_NAMESPACE

# Enable Terraform addon
https://github.com/kubevela/terraform-controller
vela addon enable terraform
```


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

For demo or test purpose, we can create predefined secret container password to be reused later.

```bash
kubectl create secret generic db-appuser \
  -n saas-workload \
  --from-literal=username=appuser \
  --from-literal=password=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c16)
```

And one for the superuser
```bash
kubectl create secret generic db-superuser \
  -n saas-workload \
  --from-literal=username=postgres \
  --from-literal=password=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c16)
```
