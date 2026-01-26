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
		// 	hub: {
		// 		db: {
		// 			type: "postgres"
		// 			password: "${dbPassword}"
		// 			url: "postgresql+psycopg2://${dbUser}@${dbHost}:5432/${dbName}"
		// 		}
		// 	}
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