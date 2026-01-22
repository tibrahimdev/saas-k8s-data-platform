# Develop KubeVela Addon

## Scaffold the addon
Run this command to generate your new addon on local working directory.
```bash
vela addon init my-addon
```

It will create new directory using `my-addon` as directory name. And it will look like this:
```bash
my-addon/
├── README.md
├── definitions
│   └── mytrait.cue
├── metadata.yaml
├── parameter.cue
├── resources
│   └── myresource.cue
├── schemas
│   └── myschema.yaml
├── template.cue
└── views
    └── my-view.cue
```

## Add the addon to Chartmuseum registry
More on this can be found in detail at https://kubevela.io/docs/platform-engineers/addon/addon-registry/.
