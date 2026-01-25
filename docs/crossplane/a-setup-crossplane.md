# Set Up Crossplane

## Preparation
Create namespace
```bash
kubectl create ns crossplane-system
```

Setup ghcr pull secret
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_PAT \
  --docker-email=any@email.com \
  -n crossplane-system
```

## Upbound Crossplane

Install crossplane CLI:

```bash
curl -sL "https://raw.githubusercontent.com/crossplane/crossplane/main/install.sh" | sh
```

Install
```bash
helm upgrade --install crossplane --namespace crossplane-system oci://xpkg.upbound.io/upbound/crossplane --version 2.1.3-up.1 -f artifacts/helm-values/crossplane-values.yaml
```

Port forward:

## Install Web UI

### CrossView
Add the Helm repository
```bash
helm repo add crossview https://corpobit.github.io/crossview
helm repo update
```
Install the chart
```bash
helm install crossview crossview/crossview \
  --namespace saas-dev \
  --set secrets.dbPassword=your-db-password \
  --set secrets.sessionSecret=$(openssl rand -base64 32)
```

### komoplane
Add the Helm repository
```bash
helm repo add komodorio https://helm-charts.komodor.io
helm repo update komodorio
```

Install
```bash
helm upgrade --install komoplane komodorio/komoplane \
  --namespace saas-dev \
  --set imagePullSecrets[0].name=docker-secret
```


## Develop Crossplane Package (XRD)

Create a new directory, let's call it `saas`. Inside that directory, add one file called `crossplane.yaml`.
```yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: saas
spec:
  crossplane:
    version: ">=2.1.3"
```

### Attach secret to Crossplane ServiceAccount

Patch the Crossplane SA:
```bash
kubectl patch serviceaccount crossplane \
  -n crossplane-system \
  -p '{
    "imagePullSecrets": [
      { "name": "ghcr-pull-secret" }
    ]
  }'

kubectl patch deployment crossplane \
  -n crossplane-system \
  --type=json \
  -p='[
    {
      "op": "add",
      "path": "/spec/template/spec/imagePullSecrets",
      "value": [{"name": "ghcr-creds"}]
    }
  ]'
```

Verify:
```bash
kubectl get sa crossplane -n crossplane-system -o yaml
```

You should see:
```yaml
imagePullSecrets:
  - name: ghcr-pull-secret
```

Next, we ship
From inside the saas/ directory:
```bash
crossplane xpkg build
```

Apply a Configuration install:
```yaml
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: saas
spec:
  package: ghcr.io/your-org/saas:v0.0.1
```

You will see in crossplane web UI that in https://your-crossplane-host/packages/configuration saas is installed and healthy.


## Uninstall Crossplane

```bash
# Helm
helm uninstall crossplane --namespace crossplane-system
```