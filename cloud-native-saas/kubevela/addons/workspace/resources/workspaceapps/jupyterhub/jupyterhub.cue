package main

jupyterhubComponents: *[] | [...{...}]

if parameter.jupyterhub.enabled {
	if parameter.jupyterhub.db.provider == "kubernetes" {
		jupyterhubComponents: [
			jupyterhubKubernetesDb,
			jupyterhub,
		]
	}
}

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
				superuserSecret: name: parameter.jupyterhub.db.cnpg.superuserSecretName
				enableSuperuserAccess: parameter.jupyterhub.db.cnpg.enableSuperuserAccess
				bootstrap: {
					initdb: {
						database: parameter.jupyterhub.db.cnpg.database
						owner:    parameter.jupyterhub.db.cnpg.owner
						secret: name: parameter.jupyterhub.db.cnpg.secretName
					}
				}
			}
		},
	]
}

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

		valuesFrom: [
			{
				kind: "Secret"
				name: "jupyterhub-helm-values"
				// +usage=ValuesKey is the data key where the values.yaml or a specific 
				// value can be found at. Defaults to 'values.yaml'.
				// valuesKey: ""
				// +usage=TargetPath is the YAML dot notation path the value should be 
				// merged at. When set, the ValuesKey is expected to be a single flat value. 
				// Defaults to 'None', which results in the values getting merged at the root.
				// targetPath: ""
			}
		]
		// values: {
		// 	fullnameOverride: "jupyterhub"
		// 	// hub: {
		// 	// 	db: {
		// 	// 		type:     "postgres"
		// 	// 		password: "password"
		// 	// 		url:      "postgresql+psycopg2://appuser@jupyterhub-db-rw.saas-workload.svc.cluster.local:5432/jupyterhub"
		// 	// 	}
		// 	// }
		// 	//   proxy: {
		// 	//     service: {
		// 	// 			type: "LoadBalancer"
		// 	// 		}
		// 	// }
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

// TODO: Using this step is causing only read-db-secret is executed.
// jupyterhubSteps: *[] | [...{...}]
// jupyterhubSteps: [
// 	{
// 		type: "read-object"
// 		name: "read-db-secret"
// 		properties: {
// 			apiVersion: "v1"
// 			kind:       "Secret"
// 			name:       parameter.jupyterhub.db.cnpg.secretName
// 		}
// 		outputs: [
// 			{},
// 		]
// 	},
// ]
