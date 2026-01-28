# Creating New KubeVela Addon

## Example: Workspace Addon
Example use case creating Workspace addon.

### Scaffold The Code

```bash
# vela addon init your-addon-name
vela addon init workspace
```

## Example: Jupyterhub Addon
Example use case creating Jupyterhub addon.

### Scaffold The Code

```bash
# vela addon init your-addon-name
vela addon init jupyterhub
```

## Push Addon
### Push To github.io

This requires you to have one github.io page. Let's assume you have this https://youruser.github.io

```bash
# Package
helm package ./jupyterhub -d ~/your-local/directory/youruser.github.io/kubevela/addons/

# Update inndex
helm repo index ~/your-local/directory/youruser.github.io/kubevela/addons/ --url https://youruser.github.io/kubevela/addons/

# cd to ~/your-local/directory/youruser.github.io
# The commit and push
```

On that, you can check the `index.yaml` should be served on https://youruser.github.io/kubevela/addons/index.yaml.