# NGINX Artifact Repository

## Overview

## KubeVela Helm Chart
Due to some issues with existing official KubeVela Helm Chart. I decided to maintain a vendored `vela-core` chart located at `artifacts/charts/vela-core` directory.

Following is the activities required upon updating the chart:

### 1. Update the chart values and templates on artifacts/charts/vela-core directory

Once code update done

### 2. Bump version on Chart.yaml
As standard, increase the last digit
  From : version: 1.10.6-saas.1
  To   : version: 1.10.6-saas.2 (+1)

* `version` → Helm chart version (semver)
* `appVersion` → application version (informational)

### 3. Package the chart into a `.tgz` artifact:

```bash
helm package artifacts/charts/vela-core --destination artifacts/charts
```

Result:

```text
artifacts/charts/
├── vela-core/
└── vela-core-1.10.6-saas.1.tgz
```

### 4. Generate or Update `index.yaml` (Publishing Step)

```bash
helm repo index artifacts --url https://saas.test
```

This will update the `index.yaml` which contains:

* chart names
* available versions
* download URLs
* SHA256 digests

⚠️ **Important rule**

> `index.yaml` is **generated during publishing** and must never be edited manually.


5. Add the Helm Repository (Client Side)

Consumers add the repository:

```bash
helm repo add saas https://saas.test
helm repo update
```

Helm performs:

```text
GET /index.yaml
```

The file is cached locally by Helm.

6. Install the Chart

Install normally:

```bash
helm install vela-core saas/vela-core \
  --namespace saas-system \
  --create-namespace
```

7. Upgrade the Chart

To release a new version:

1. Bump `Chart.yaml` version
2. Re-package the chart
3. Re-run `helm repo index`
4. Publish updated artifacts

Clients upgrade with:

```bash
helm upgrade vela-core saas/vela-core
```
