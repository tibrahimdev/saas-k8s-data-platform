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
vela install --version ${KUBEVELA_VERSION}
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

Delete all CRD from cluster using
```bash
kubectl get crd |grep oam | awk '{print $1}' | xargs kubectl delete crd
```
