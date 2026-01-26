package main

jupyterhubKubernetesDb: {
	name: "jupyterhub-db"
	type: "k8s-objects"
	properties: objects: [
		{
			apiVersion: "postgresql.cnpg.io/v1"
			kind:       "Cluster"
			metadata: {
				name:      "jupyterhub-db"
				namespace: parameter.jupyterhub.namespace
			}
			spec: {
				instances: parameter.jupyterhub.db.cnpg.instances
				storage: {
					size: parameter.jupyterhub.db.storageSize
				}
				// bootstrap: {
				//   initdb: {
				//     database: "jupyterhub"
				//     owner:   "jupyterhub"
				//   }
				// }
			}
		}
	]
}

