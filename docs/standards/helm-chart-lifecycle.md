## Helm Chart Lifecycle: From Source to NGINX Artifact Repository

This section describes the complete lifecycle of a Helm chart, from initial creation to being published and consumed from a **static, read-only NGINX artifact repository**.

This model intentionally avoids ChartMuseum and any server-side mutation. All writes happen **before publishing**, and all serving is **read-only**.

---

### 1. Create a New Helm Chart

Create a chart using Helm’s built-in scaffolding:

```bash
helm create saas-core
```

Generated structure:

```text
saas-core/
├── Chart.yaml
├── values.yaml
├── charts/
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── _helpers.tpl
```

Edit `Chart.yaml`:

```yaml
apiVersion: v2
name: saas-core
description: SaaS Control Plane Core Components
type: application
version: 1.1.1
appVersion: "1.1.1"
```

* `version` → Helm chart version (semver)
* `appVersion` → application version (informational)

---

### 2. Place Charts in the Artifact Source Tree

Charts should live in a **source directory**, not directly in the served repository.

Recommended layout:

```text
artifacts/
└── charts/
    └── saas-core/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

This separates:

* **mutable source charts**
* **immutable packaged artifacts**

---

### 3. Package the Helm Chart (Artifact Creation)

Package the chart into a `.tgz` artifact:

```bash
helm package artifacts/charts/saas-core --destination artifacts/charts
```

Result:

```text
artifacts/charts/
├── saas-core/
└── saas-core-1.1.1.tgz
```

The `.tgz` file is the **only artifact Helm installs**.

---

### 4. Generate or Update `index.yaml` (Publishing Step)

Generate the Helm repository index:

```bash
helm repo index artifacts --url https://saas.test
```

This produces:

```text
artifacts/
├── index.yaml
└── charts/
    └── saas-core-1.1.1.tgz
```

`index.yaml` contains:

* chart names
* available versions
* download URLs
* SHA256 digests

⚠️ **Important rule**

> `index.yaml` is **generated during publishing** and must never be edited manually.

---

### 5. Write vs Read Responsibility (Critical Clarification)

There are **two distinct phases** in the Helm lifecycle.

#### Publishing phase (write access)

This happens:

* on a developer machine, or
* in CI/CD

During this phase:

* `helm package` creates `.tgz`
* `helm repo index` **overwrites or updates `index.yaml`**

```text
Developer / CI
   |
   v
artifacts/
├── index.yaml   ← written here
└── charts/*.tgz
```

This directory is **mutable only at build time**.

---

#### Serving phase (read-only)

Once published, artifacts are served by NGINX:

```text
NGINX
  |
  v
/artifacts (mounted read-only)
```

NGINX:

* never modifies files
* serves static content only
* can safely mount the directory as `read-only`

Helm clients **never write** to the repository.

---

### 6. Serve Artifacts via NGINX (Static Origin)

Filesystem served by NGINX:

```text
/srv/saas/
├── index.yaml
├── bootstrap.sh
├── bootstrap-manifest.yaml
└── charts/
    └── saas-core-1.1.1.tgz
```

NGINX performs:

* no Helm logic
* no mutation
* no API handling

It only serves files.

---

### 7. Add the Helm Repository (Client Side)

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

---

### 8. Install the Chart

Install normally:

```bash
helm install saas-core saas/saas-core \
  --namespace saas-system \
  --create-namespace
```

Helm:

1. reads `index.yaml`
2. selects the latest version
3. downloads the `.tgz`
4. verifies the digest
5. installs

No server-side changes occur.

---

### 9. Upgrade the Chart

To release a new version:

1. Bump `Chart.yaml` version
2. Re-package the chart
3. Re-run `helm repo index`
4. Publish updated artifacts

Clients upgrade with:

```bash
helm upgrade saas-core saas/saas-core
```

---

### Immutability Rules (Strongly Recommended)

* Never modify an existing `.tgz`
* Never delete published versions
* Always publish a new version
* Treat `index.yaml` as generated metadata

This guarantees:

* reproducible installs
* safe rollbacks
* deterministic bootstrap

### Why This Works with Read-Only NGINX

Helm repositories are **static by design**.

A valid Helm repo requires only:

* `index.yaml`
* `.tgz` chart archives
* HTTP(S) access

Helm **never performs writes** to a repository.

This is why:

* GitHub Pages
* S3 static hosting
* Cloudflare Pages
* NGINX

all work seamlessly.
