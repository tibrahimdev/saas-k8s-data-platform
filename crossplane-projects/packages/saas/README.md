# SaaS Project

This repository contains a **Crossplane Composition and XR** for bootstrapping a SaaS environment.

```bash
# TODO: directory structure explanation
```

## Prerequisites

- Kubernetes cluster
- Crossplane installed
- Required Functions installed (e.g., `patch-and-transform`)

## Quickstart

1. Install required namespace:

```bash
kubectl create namespace saas-system
```

2. Install required Crossplane Functions:

```bash
kubectl apply -f https://example.com/function-patch-and-transform.yaml
```

3. Build and push the package:

```bash
make build
make push
```

4. Apply the SaaSBootstrap XR:

```bash
kubectl apply -f saas-bootstrap-xr.yaml
```

5. Check the bootstrap status:

```bash
kubectl get configmap -n saas-system
```

## Structure

```
.
├── Makefile          # Build, push, and future commands
├── crossplane.yaml   # Composition definition
└── README.md
```

## Notes

* The Composition does **not create resources by itself** — you must instantiate the `SaaSBootstrap` XR.
* Functions and providers must be installed in the cluster beforehand.
* Namespace `saas-system` must exist before applying resources.
