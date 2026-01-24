package main

output: {
	apiVersion: "core.oam.dev/v1beta1"
	kind:       "Application"
	spec: {
    components: [

      // Jupyterhub
      if parameter.jupyterhub.enabled {
        jupyterhub_db_cnpg
      }
      if parameter.jupyterhub.enabled {
        jupyterhub
      }
    ]

    policies: []
  }
}
