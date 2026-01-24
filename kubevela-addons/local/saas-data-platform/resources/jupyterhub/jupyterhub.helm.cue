package main

jupyterhub: {
	name: "jupyterhub"
	type: "helm"
	// dependsOn: ["cert-manager-ns"]
	properties: {
		repoType:        "helm"
		url:             "https://jupyterhub.github.io/helm-chart/"
		chart:           "jupyterhub"
		targetNamespace: parameter.jupyterhub.namespace
		version:         "4.3.2"
		values:
			fullnameOverride: "jupyterhub"
      proxy:
        service:
          type: "LoadBalancer"
	}
}
