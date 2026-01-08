# Deploy on K3s

## Installing K3s

Follow instruction on https://docs.k3s.io/quick-start.

K3s provides an installation script that is a convenient way to install it as a service on systemd or openrc based systems. This script is available at [https://get.k3s.io](https://get.k3s.io). To install K3s using this method, just run:

=== "Linux/Mac"
    ```bash
    curl -sfL https://get.k3s.io | sh -
    ```


After running this installation:

- The K3s service will be configured to automatically restart after node reboots or if the process crashes or is killed
- Additional utilities will be installed, including `kubectl`, `crictl`, `ctr`, `k3s-killall.sh`, and `k3s-uninstall.sh`
- A [kubeconfig](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/) file will be written to `/etc/rancher/k3s/k3s.yaml` and the `kubectl` installed by K3s will automatically use it.

## Accessing K3s Cluster

=== "Linux/Mac"
    ```bash
    sudo install -m 600 -o "$USER" -g "$USER" \
      /etc/rancher/k3s/k3s.yaml \
      ~/.kube/k3s.yaml
    ```

Use it via KUBECONFIG

=== "Linux/Mac"
    ```bash
    export KUBECONFIG=~/.kube/k3s.yaml
    ```

Then use `kubectl` or `k9s` like usual.

=== "Linux/Mac"
    ```bash
    kubectl get namespaces
    ```

