# Setting Up KubeVela

## Install KubeVela CLI
Reference: https://kubevela.io/docs/installation/kubernetes/#install-vela-cli

> This step will be part of automated `cluster-bootstrap` process.

For example using bash
```bash
curl -fsSl https://kubevela.io/script/install.sh | bash
```

## Install KubeVela Core

> This step will be part of automated `cluster-bootstrap` process.

Now we need to install KubeVela Core into the Kubernetes cluster.

```bash
export KUBEVELA_VERSION=1.10.6
helm repo add kubevela https://kubevela.github.io/charts
helm repo update
helm install --create-namespace -n vela-system kubevela kubevela/vela-core --wait --version $KUBEVELA_VERSION
```

## Install VelaUX and other addons
> This step will be part of automated `cluster-bootstrap` process.
```bash
vela addon enable velaux
vela addon enable fluxcd
```

## Uninstall Kubevela
```bash
vela uninstall --force
```
