package main

jupyterhub_db_cnpg: {
  name: "jupyterhub-cnpg"
  type: "k8s-objects"
  properties: {
    objects: [{
      apiVersion: "postgresql.cnpg.io/v1"
      kind:       "Cluster"
      metadata: {
        name:      "jupyterhub-db"
        namespace: parameter.jupyterhub.namespace
      }
      spec: {
        instances: 1
        storage: {
          size: "10Gi"
        }
        // bootstrap: {
        //   initdb: {
        //     database: "jupyterhub"
        //     owner:   "jupyterhub"
        //   }
        // }
      }
    }]
  }
  
}
