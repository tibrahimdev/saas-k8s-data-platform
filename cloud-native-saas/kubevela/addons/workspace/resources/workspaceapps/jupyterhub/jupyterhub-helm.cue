package main

jupyterhub: {
	name: "jupyterhub"
	type: "helm"
	dependsOn: ["jupyterhub-db"]
	properties: {
		repoType:        "helm"
		url:             "https://jupyterhub.github.io/helm-chart/"
		chart:           "jupyterhub"
		targetNamespace: parameter.jupyterhub.namespace
		version:         parameter.jupyterhub.version
		values:
			fullnameOverride: "jupyterhub"
			hub: {
				db: {
					type: "postgres"
					password: parameter.jupyterhub.db.password
					url: "postgresql+psycopg2://jupyterhub@$jupyterhub-db-rw.saas-workload.svc.cluster.local:5432/jupyterhub"
				}
			}
    //   proxy: {
    //     service: {
		// 			type: "LoadBalancer"
		// 		}
			// }
	}
	// traits: [
	// 	{
	// 		type: "read-secret"
	// 		properties: {
	// 			secret: {
	// 				name: "jupyterhub-db-app"
	// 				namespace: parameter.jupyterhub.namespace
	// 			}
	// 			mapping: {}
	// 		}
	// 	}
	// ]
}

jupyterhubSteps: *[] | [...{...}]
jupyterhubSteps: [
	{
		type: "read-object"
		name: "read-db-secret"
		properties: {
			apiVersion: "v1"
			kind: "Secret"
			name: "jupyterhub-db-app"
		}
		outputs: [
			{
				
			}
		]
	}
]