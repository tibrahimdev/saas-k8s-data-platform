package main

_targetNamespace: parameter.namespace

// _jupyterhubComponents: [...] | []
// if parameter.jupyterhub.enabled {
// 	if parameter.jupyterhub.db.provider == "kubernetes" {
// 		_jupyterhubComponents: [
// 			jupyterhub,
// 			jupyterhubKubernetesDb,
// 		]
// 	}
// } else {
// 	_jupyterhubComponents: []
// }

// _jupyterhubComponents: [
// 	jupyterhub,
// 	jupyterhubKubernetesDb,
// ]

output: {
	apiVersion: "core.oam.dev/v1beta1"
	kind:       "Application"
	spec: {
		components: [
			{
				type: "k8s-objects"
				name: "workspace-secret"
				properties: objects: [{
					apiVersion: "v1"
					kind:       "Secret"
					metadata: {
						name:      "workspace-secret"
						namespace: _targetNamespace
					}
				}]
			},

			// if parameter.jupyterhub.enabled {jupyterhub},

		] + jupyterhubComponents

		policies: []

		workflow: steps: []
	}
}
