# Develop Crossplane

```bash
cd crossplane-projects/saas/devel
```

## Install prerequisite

```bash
kubectl apply -f 
```

## Workspace

```bash
# Deploy workspace Composite Resource Definition (XRD)
kubectl apply -f xrds/workspace.xrd.yaml

# Check the created XRD
k get compositeresourcedefinition

# Deploy workspace Composition
kubectl apply -f comps/workspace.comp.yaml

# Create a workspace by deploying Composite Resource (XR)
kubectl apply -f xrs/workspace.xr.yaml
```
