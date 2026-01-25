# Workspaces

## Development

```bash
# Deploy workspace Composite Resource Definition (XRD)
kubectl apply -f crossplane/packages/workspace/workspace.definition.yaml

# Check the created XRD
kubectl get compositeresourcedefinition

# Deploy workspace Composition
kubectl apply -f crossplane/packages/workspace/workspace.composition.yaml

# Check the created composition
kubectl get composition

# Create a workspace by deploying Composite Resource (XR)
kubectl apply -f crossplane/examples/workspace.yaml

# Check the created workspace XR
kubectl get workspace -A
```

## Packaging
TODO
