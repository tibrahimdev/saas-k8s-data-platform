# Install kind

```bash
go install sigs.k8s.io/kind@v0.31.0
```
## Creating kind Cluster

For example, let’s say you create two clusters:
```bash
kind create cluster # Default cluster context name is `kind`.
...
kind create cluster --name saas
```

When you list your kind clusters, you will see something like the following:
```bash
kind get clusters
kind
saas
```

In order to interact with a specific cluster, you only need to specify the cluster name as a context in kubectl:
```bash
kubectl cluster-info --context kind-kind
kubectl cluster-info --context kind-saas
```

Also if above command not working, can use this to set kubernetes context:
```bash
kind export kubeconfig --name saas --kubeconfig "$KUBECONFIG"
```

After that you can start interact using `kubectl` or `k9s`.

To show current cluster + context that you're CLI working on:
```bash
kubectl config current-context
```

## Deleting a Cluster
If you created a cluster with kind create cluster then deleting is equally simple:
```bash
kind delete cluster
```
If the flag `--name` is not specified, kind will use the default cluster context name kind and delete that cluster.

Note: By design, requesting to delete a cluster that does not exist will not return an error. This is intentional and is a means to have an idempotent way of cleaning up resources.

## Loading an Image Into Your Cluster
You can load one or more images into your kind cluster:
```bash
kind load docker-image my-app:latest
kind load docker-image my-app:latest my-db:latest my-cache:latest
```

Note: If using a named cluster you will need to specify the name of the cluster:
```bash
kind load docker-image my-app:latest --name test-cluster
```
