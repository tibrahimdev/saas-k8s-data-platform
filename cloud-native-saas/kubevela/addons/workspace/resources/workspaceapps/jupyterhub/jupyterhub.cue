package main

jupyterhubComponents: *[] | [...{...}]

if parameter.jupyterhub.enabled {
	if parameter.jupyterhub.db.provider == "kubernetes" {
		jupyterhubComponents: [jupyterhubKubernetesDb, jupyterhub]
	}
}
