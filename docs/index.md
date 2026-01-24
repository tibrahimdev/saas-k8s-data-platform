# Welcome to SaaS K8s Data Platform

## Quickstart

### TODO

Yes — that’s **clear and professional**, but you can polish it slightly to make it more formal and **highlight interactivity / token usage**. Here’s a refined version for a README:

---

### Bootstrap Tenant Cluster

To initialize the tenant cluster, run the bootstrap script on the tenant side:

```bash
# Replace <token> with the tenant bootstrap token
BOOTSTRAP_TOKEN=replace-with-tenant-token \
  bash <(curl -fsSL https://saas.test/bootstrap-cluster.sh)
```
