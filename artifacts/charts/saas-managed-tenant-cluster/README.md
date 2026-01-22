# Managed Tenant Cluster Helm Chart

Bootstrap SaaS-managed tenant clusters with system namespace protection.

## Install

Add and update the repo
```bash
helm repo add saas https://saas.test
helm repo update
```

Default safe install:
```sh
helm install managed-cluster saas/managed-tenant-cluster
```

Custom prefix:

```sh
helm install tenant ./managed-tenant-cluster --set prefix=mytenant
```

Enable break-glass:

```sh
helm install tenant ./managed-tenant-cluster --set breakGlassEnabled=true
```

Uninstalling:
```bash
helm uninstall managed-cluster
```

## Behavior

* System namespace: protected
* Workload namespace: normal
* Break-glass: optional, must be explicitly set

## Usage examples

### Default install

```sh
helm install tenant ./managed-tenant-cluster
```

Creates:

* `saas-system` (protected)
* `saas-workload`

### Custom prefix + break-glass

```sh
helm install tenant ./managed-tenant-cluster \
  --set prefix=tenant123 \
  --set breakGlassEnabled=true
```

Creates:

* `tenant123-system` (protected, break-glass capable)
* `tenant123-workload`

Deletion of `system` now **requires**:

```sh
kubectl label namespace tenant123-system saas.test/breakglass=true
kubectl delete namespace tenant123-system
```
