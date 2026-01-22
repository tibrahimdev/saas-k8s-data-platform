# Install Local Kubernetes Clusters

## Using Kind
### Install kind

```bash
go install sigs.k8s.io/kind@v0.31.0
```
### Creating kind Cluster

Since we're about to replicate as much as we can with production grade clusters, we will
use the YAML config file so we can configure more.

```bash
cd clusters/kind/

# Creating SaaS cluster

# Creating Tenant cluster
kind create cluster --config=kind-saas-tenant-cluster.yaml
```

When you list your kind clusters, you will see something like the following:
```bash
kind get clusters
kind
saas-tenant-test
```

In order to interact with a specific cluster, you only need to specify the cluster name as a context in kubectl:
```bash
kubectl cluster-info --context kind-saas-tenant-test
```

Also if above command not working, can use this to set kubernetes context:
```bash
kind export kubeconfig --name saas-tenant-test --kubeconfig "$KUBECONFIG"
```

After that you can start interact using `kubectl` or `k9s`.

To show current cluster + context that you're CLI working on:
```bash
kubectl config current-context
```

### Adding labels and taints

Adding labels:
```bash
kubectl label node saas-tenant-test-worker node-role.kubernetes.io/default=
kubectl label node saas-tenant-test-worker2 node-role.kubernetes.io/database=
```

```bash
# All database workload must use "saas-tenant-test-worker2"
kubectl taint nodes saas-tenant-test-worker2 workload=database:NoSchedule
```

### Deleting a Kind Cluster
If you created a cluster with kind create cluster then deleting is equally simple:
```bash
kind delete cluster

# with specific name
kind delete cluster --name saas-tenant-test
```
If the flag `--name` is not specified, kind will use the default cluster context name kind and delete that cluster.

Note: By design, requesting to delete a cluster that does not exist will not return an error. This is intentional and is a means to have an idempotent way of cleaning up resources.

### Loading an Image Into Kind Cluster
You can load one or more images into your kind cluster:
```bash
kind load docker-image my-app:latest
kind load docker-image my-app:latest my-db:latest my-cache:latest
```

Note: If using a named cluster you will need to specify the name of the cluster:
```bash
kind load docker-image my-app:latest --name test-cluster
```

## Using Minikube
### Install Minikube
Follow instruction on https://minikube.sigs.k8s.io/docs/start/.

### Creating Minikube Clusters

```bash
# Creating SaaS cluster with named cluster "saas-minikube"
minikube start -p saas-minikube

# Creating SaaS cluster with named cluster "saas-minikube"
# And adjust cpus memory limit
minikube start -p saas-minikube --cpus=4 --memory=8192
```

On WSL2 (experimental - see [#5392](https://github.com/kubernetes/minikube/issues/5392)), you may need to run:
```bash
sudo mkdir /sys/fs/cgroup/systemd && sudo mount -t cgroup -o none,name=systemd cgroup /sys/fs/cgroup/systemd
```

### Deleting Minikube Cluster
```bash
minikube delete -p saas-minikube
```

---

## Bootstrap the cluster
We have convenient script to bootstrap the cluster located at `scripts/bootstrap-cluster.sh`.

```bash
WORKSPACE=ws1 BOOTSTRAP_TOKEN=mytoken ./scripts/bootstrap-cluster.sh
```
